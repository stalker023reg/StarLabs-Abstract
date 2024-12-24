import asyncio
import random
import time
from eth_account.messages import encode_defunct
import noble_tls
from eth_typing import HexStr
from loguru import logger
from web3 import AsyncWeb3, AsyncHTTPProvider, Web3
from web3.contract import AsyncContract
from web3.exceptions import Web3Exception

from extra import constants


class MyWeb3:
    def __init__(self, rpc: str, client: noble_tls.Session):
        self.web3 = AsyncWeb3(
            AsyncHTTPProvider(rpc, request_kwargs={"verify_ssl": False})
        )
        self.http_client = client

    async def wait_for_transaction_receipt(
        self, transaction_hash, timeout=120, poll_latency=3
    ):
        start_time = time.time()
        while True:
            try:
                receipt = await self.web3.eth.get_transaction_receipt(transaction_hash)
                if receipt:
                    return receipt
            except Exception as err:
                str_err = str(err)
                if "not found" in str(err):
                    pass
                else:
                    raise Exception(str_err)

            if time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for transaction receipt")

            time.sleep(poll_latency)

    async def get_eth_balance(self, address: str) -> dict:

        balance_wei = await self.web3.eth.get_balance(
            self.web3.to_checksum_address(address)
        )
        balance_eth = self.web3.from_wei(balance_wei, "ether")

        return {"balance_wei": balance_wei, "balance_eth": balance_eth}

    async def make_request(
        self,
        method: str = "GET",
        url: str = None,
        headers: dict = None,
        params: dict = None,
        data: str = None,
        json: dict = None,
    ):

        headers = (headers or {}) | {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3"
        }
        response = await self.http_client.execute_request(
            method=method, url=url, headers=headers, data=data, params=params, json=json
        )

        try:
            data = response.json()

            if response.status_code == 200:
                return data
            raise Exception(
                f"Bad request to Odos API. "
                f"Response status: {response.status_code}. Response: {response.text}"
            )
        except Exception as error:
            raise Exception(
                f"Bad request to Odos API. "
                f"Response status: {response.status_code}. Response: {response.text} Error: {error}"
            )

    async def prepare_transaction(self, address, value: int = 0) -> dict:
        try:
            tx_params = {
                "chainId": 1,
                "from": self.web3.to_checksum_address(address),
                "nonce": await self.web3.eth.get_transaction_count(address),
                "value": value,
            }

            base_fee = await self.web3.eth.gas_price
            max_priority_fee_per_gas = await self.get_priority_fee()
            max_fee_per_gas = int(base_fee + max_priority_fee_per_gas * 1.05 * 1.1)

            if max_priority_fee_per_gas > max_fee_per_gas:
                max_priority_fee_per_gas = int(max_fee_per_gas * 0.95)

            tx_params["maxPriorityFeePerGas"] = max_priority_fee_per_gas
            tx_params["maxFeePerGas"] = int(max_fee_per_gas * 1.2)
            tx_params["type"] = "0x2"

            return tx_params
        except Exception as error:
            raise Exception(f"{address} | Prepare transaction err: {error}")

    async def get_priority_fee(self) -> int:
        fee_history = await self.web3.eth.fee_history(5, "latest", [20.0])
        non_empty_block_priority_fees = [
            fee[0] for fee in fee_history["reward"] if fee[0] != 0
        ]

        divisor_priority = max(len(non_empty_block_priority_fees), 1)

        priority_fee = int(round(sum(non_empty_block_priority_fees) / divisor_priority))

        return priority_fee

    async def send_transaction(
        self,
        address,
        private_key,
        transaction=None,
        need_hash: bool = False,
        poll_latency: int = 10,
        timeout: int = 360,
        tx_hash=None,
        send_mode: bool = False,
        signed_tx=None,
    ) -> bool | HexStr:
        try:
            gas = int((await self.web3.eth.estimate_gas(transaction)) * 1.25)
            transaction["gas"] = gas
        except Exception as error:
            raise Exception(f"{address} | Send transaction failed: {error}")

        if not tx_hash:
            try:
                if not send_mode:
                    signed_tx = self.web3.eth.account.sign_transaction(
                        transaction, private_key
                    ).rawTransaction
                tx_hash = Web3.to_hex(
                    await self.web3.eth.send_raw_transaction(signed_tx)
                )
            except Exception as error:
                if self.get_normalize_error(error) == "already known":
                    logger.warning(f"{address} | RPC got error, but tx was send")
                    return True
                else:
                    raise BlockchainException(f"{self.get_normalize_error(error)}")

        total_time = 0
        while True:
            try:
                await asyncio.sleep(25)

                receipts = await self.web3.eth.get_transaction_receipt(tx_hash)
                status = receipts.get("status")
                if status == 1:
                    message = f"{address} | Transaction was successful: {constants.ETH_EXPLORER_TX}{tx_hash}"
                    logger.success(message)
                    if need_hash:
                        return tx_hash
                    return True
                elif status is None:
                    await asyncio.sleep(poll_latency)
                else:
                    raise Exception(
                        f"Transaction failed: {constants.ETH_EXPLORER_TX}{tx_hash}"
                    )
            except TransactionNotFound:
                if total_time > timeout:
                    raise BlockchainException(
                        f"Transaction is not in the chain after {timeout} seconds"
                    )
                total_time += poll_latency
                await asyncio.sleep(poll_latency)

            except Exception as error:
                if "Transaction failed" in str(error):
                    raise BlockchainException(
                        f"Transaction failed: {constants.ETH_EXPLORER_TX}{tx_hash}"
                    )
                logger.warning(
                    f"{address} | RPC got autism response. Error: {error}",
                    type_msg="warning",
                )
                total_time += poll_latency
                await asyncio.sleep(poll_latency)

    async def make_approve(
        self,
        my_address: str,
        abi,
        private_key: str,
        token_address: str,
        spender_address: str,
        amount_in_wei: int,
    ) -> bool:
        logger.info(f"{my_address} | Approving token {token_address}.")
        transaction = (
            await self.get_contract(token_address, abi)
            .functions.approve(
                self.web3.to_checksum_address(spender_address), amount_in_wei
            )
            .build_transaction(await self.prepare_transaction(my_address))
        )

        return await self.send_transaction(my_address, private_key, transaction)

    def get_contract(self, contract_address: str, abi: dict) -> AsyncContract:
        return self.web3.eth.contract(
            address=AsyncWeb3.to_checksum_address(contract_address), abi=abi
        )

    async def get_allowance(
        self, token_address: str, my_address, spender_address: str, abi
    ) -> int:
        contract = self.get_contract(token_address, abi)
        return await contract.functions.allowance(
            self.web3.to_checksum_address(my_address),
            self.web3.to_checksum_address(spender_address),
        ).call()

    async def check_for_approved(
        self,
        my_address: str,
        abi,
        private_key,
        token_address: str,
        spender_address: str,
        amount_in_wei: int,
        without_bal_check: bool = False,
    ) -> bool:
        try:
            contract = self.get_contract(token_address, abi)

            balance_in_wei = await contract.functions.balanceOf(spender_address).call()
            symbol = await contract.functions.symbol().call()

            logger.info(f"{my_address} | Check for approval {symbol}")

            if not without_bal_check and balance_in_wei <= 0:
                raise Exception(f"{my_address} | Zero {symbol} balance")

            approved_amount_in_wei = await self.get_allowance(
                token_address=token_address,
                my_address=my_address,
                spender_address=spender_address,
                abi=abi,
            )

            if amount_in_wei <= approved_amount_in_wei:
                logger.success(f"{my_address} | Token {symbol} already approved")
                return True

            result = await self.make_approve(
                my_address,
                abi,
                private_key,
                token_address,
                spender_address,
                amount_in_wei,
            )

            await asyncio.sleep(random.randint(5, 9))
            return result
        except Exception as error:
            raise BlockchainException(f"{self.get_normalize_error(error)}")

    async def check_gas(self, minimum_gas_eth):
        while True:
            try:
                current_gas_price_wei = await self.web3.eth.gas_price
                current_gas_price_gwei = current_gas_price_wei / 1e9
                logger.info(f"Current gas price: {current_gas_price_gwei} Gwei")

                if current_gas_price_gwei <= minimum_gas_eth:
                    logger.info(
                        "Gas price is within the limit. Proceeding with the transaction."
                    )
                    break
                else:
                    logger.info(
                        f"Gas price is too high: {current_gas_price_gwei} Gwei. Waiting for 20 seconds to recheck."
                    )
                    time.sleep(20)
            except Exception as e:
                logger.error(f"Error checking gas price: {e}")
                time.sleep(20)

    @staticmethod
    def get_normalize_error(error: Exception) -> Exception | str:
        try:
            if isinstance(error.args[0], dict):
                error = error.args[0].get("message", error)
            return error
        except:
            return error

    async def get_token_balance(
        self, abi: dict, sender_address: str, token_address: str = None
    ) -> [float, int, str]:
        await asyncio.sleep(3)

        contract = self.get_contract(token_address, abi)
        amount_in_wei = await contract.functions.balanceOf(
            self.web3.to_checksum_address(sender_address)
        ).call()
        decimals = await contract.functions.decimals().call()

        symbol = await contract.functions.symbol().call()

        return amount_in_wei, amount_in_wei / 10**decimals, symbol

    async def get_signature(self, message: str, private_key: str):
        encoded_msg = encode_defunct(text=message)
        signed_msg = Web3().eth.account.sign_message(
            encoded_msg, private_key=private_key
        )
        signature = signed_msg.signature.hex()

        return signature


class TransactionNotFound(Web3Exception):
    """
    Raised when a tx hash used to lookup a tx in a jsonrpc call cannot be found.
    """

    pass


class BlockchainException(Exception):
    pass
