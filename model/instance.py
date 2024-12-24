import asyncio
import base64
from datetime import datetime, timezone
import hashlib
import random
import secrets
import string
import traceback
from urllib.parse import unquote
import web3
import eth_account
from loguru import logger
from noble_tls import Session

from extra import constants
from extra.client import create_client, create_twitter_client
from model.utils.browser import CreateBrowserInstance
from model.utils.captcha import Capsolver, TwoCaptcha
from model.utils.utils import retry
from model.utils.web_3 import MyWeb3


class Abstract:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        twitter_token: str,
        config: dict,
    ):
        self.account_index = account_index
        self.proxy = proxy
        self.config = config
        self.private_key = private_key
        self.twitter_token = twitter_token

        self.wallet = eth_account.Account.from_key(self.private_key)
        self.address = self.wallet.address
        self.client: Session | None = None
        self.web3: MyWeb3 | None = None

        self.login_tokens = {
            "bearer_token": "",
            "privy_access_token": "",
            "refresh_token": "",
            "identity_token": "",
            "userLogin": "",
        }

    async def initialize(self) -> bool:
        try:
            self.client = await create_client(self.proxy)
            self.web3 = MyWeb3(
                random.choice(self.config["bridge"]["sepolia_rpc"]), self.client
            )
            return True
        except Exception as err:
            logger.error(f"{self.address} | Error init: {err}")
            return False

    async def tasks(self) -> bool:
        try:
            success = True

            if not await self._login_abstract():
                return False

            if not await self.__is_twitter_connected():
                if not await self._connect_twitter():
                    logger.error(
                        f"{self.address} | Unable to connect twitter. Account may be blocked etc."
                    )
                    return False

            tasks = await self.__get_tasks(tasks_only=True)
            if not tasks:
                return False

            for task in tasks:
                if task["title"] in [
                    "Abstract x DeForm Commemorative NFT",
                    "Earn more raffle entries",
                    "Refer friends, earn more points!",
                    "Share the news about new quests",
                    "RT the DeForm x Abstract announcement",
                ]:
                    continue

                records = task["records"]
                if records and len(records) > 0:
                    last_record = records[len(records) - 1]

                    if last_record["status"] == "COMPLETED":
                        logger.success(
                            f'{self.address} | Task "{task["title"]}" already completed!'
                        )
                        continue

                status = await self.__do_task(task)
                if not status:
                    success = False

                pause = random.randint(
                    self.config["settings"]["random_pause_between_actions"][0],
                    self.config["settings"]["random_pause_between_actions"][1],
                )
                logger.info(
                    f"{self.address} | Sleeping for {pause} seconds between actions..."
                )
                await asyncio.sleep(pause)

            return success

        except Exception as err:
            logger.error(f"{self.address} | Error tasks: {err}")
            return False

    async def bridge_eth(self) -> bool:
        try:
            # Check wallet balance first
            balance = await self.web3.get_eth_balance(self.address)
            if balance > self.config["bridge"]["eth_to_bridge"][1]:
                logger.success(
                    f"{self.address} | Account already has enough ETH: {balance['balance_eth']}"
                )
                return True

            logger.info(
                f"{self.address} | Sepolia ETH balance: {balance['balance_eth']}"
            )

            # Get random amount from config
            eth_amount = random.uniform(
                self.config["bridge"]["eth_to_bridge"][0],
                self.config["bridge"]["eth_to_bridge"][1],
            )
            logger.info(f"{self.address} | Will try to bridge {eth_amount} ETH")

            # Check if we have enough balance
            if balance["balance_eth"] < eth_amount:
                raise Exception(
                    f"Insufficient balance: have {balance['balance_eth']} ETH, need {eth_amount} ETH"
                )

            wei_amount = self.web3.web3.to_wei(eth_amount, "ether")

            # Create contract instance using ABI from config
            contract = self.web3.web3.eth.contract(
                address=self.web3.web3.to_checksum_address(
                    "0x35A54c8C757806eB6820629bc82d90E056394C92"
                ),
                abi=self.config["bridge_abi"],
            )

            # Calculate the exact values based on the successful transaction ratios
            base_wei = wei_amount  # Use the input amount as base
            mint_value = int(
                base_wei * 1.133608357830964
            )  # Maintain the same ratio as successful tx

            # Prepare request parameters
            request = {
                "chainId": 11124,  # zkSync Era testnet
                "mintValue": mint_value,  # Calculated based on ratio
                "l2Contract": self.web3.web3.to_checksum_address(self.address),
                "l2Value": base_wei,  # Use input amount
                "l2Calldata": "0x",
                "l2GasLimit": 384513,
                "l2GasPerPubdataByteLimit": 800,
                "factoryDeps": [],
                "refundRecipient": self.web3.web3.to_checksum_address(self.address),
            }

            # Get gas estimates first
            base_fee = await self.web3.web3.eth.gas_price
            max_priority_fee = await self.web3.get_priority_fee()
            max_fee = int(
                base_fee * 1.1 + max_priority_fee
            )  # Base fee + 10% + priority fee

            # Build transaction using contract function
            transaction = await contract.functions.requestL2TransactionDirect(
                request
            ).build_transaction(
                {
                    "chainId": 11155111,  # Sepolia
                    "from": self.web3.web3.to_checksum_address(self.address),
                    "value": mint_value,  # Use mintValue as transaction value
                    "maxFeePerGas": max_fee,
                    "maxPriorityFeePerGas": max_priority_fee,
                    "type": 2,  # EIP-1559 transaction
                    "nonce": await self.web3.web3.eth.get_transaction_count(
                        self.address
                    ),
                }
            )

            # Estimate gas
            gas = await self.web3.web3.eth.estimate_gas(transaction)
            transaction["gas"] = int(gas * 1.2)  # Add 20% buffer

            # Sign and send transaction
            signed_txn = self.web3.web3.eth.account.sign_transaction(
                transaction, self.private_key
            )
            tx_hash = await self.web3.web3.eth.send_raw_transaction(
                signed_txn.raw_transaction
            )

            logger.info(
                f"{self.address} | Bridge transaction sent: {constants.SEPOLIA_EXPLORER}0x{tx_hash.hex()}"
            )

            # Wait for transaction confirmation
            await self.web3.web3.eth.wait_for_transaction_receipt(tx_hash)
            logger.success(f"{self.address} | Bridge transaction confirmed!")

            return True

        except Exception as err:
            logger.error(f"{self.address} | Error bridge: {err}")
            return False

    async def faucet(self) -> bool:
        try:
            logger.info(f"{self.address} | Requesting faucet...")

            browser = CreateBrowserInstance(self.proxy)
            await browser.start()
            await browser.page.goto(
                "https://faucet.triangleplatform.com/abstract/testnet"
            )

            # Find and fill the input field with wallet address
            await browser.page.wait_for_selector('input[type="text"]')
            await browser.page.fill('input[type="text"]', self.address)
            await asyncio.sleep(1)

            start_time = asyncio.get_event_loop().time()
            total_timeout = 300  # 5 minutes in seconds

            while asyncio.get_event_loop().time() - start_time < total_timeout:
                try:
                    # Find and click the Request button
                    request_button = await browser.page.wait_for_selector(
                        'button:has-text("Request")', timeout=3000
                    )

                    # Check if button is enabled
                    is_disabled = await request_button.get_attribute("disabled")
                    if is_disabled:
                        await asyncio.sleep(3)
                        continue

                    # Click the button if it's enabled
                    await request_button.click()
                    logger.info(f"{self.address} | Clicked Request button")

                    # Check for Success message for 10 seconds
                    try:
                        await browser.page.wait_for_selector(
                            'text="Success: "', timeout=30000
                        )
                        logger.success(
                            f"{self.address} | Successfully received tokens from faucet!"
                        )
                        await browser.stop()
                        return True
                    except:
                        logger.info(
                            f"{self.address} | Success message not found, checking for already made request..."
                        )
                        # Check for already made request message
                        try:
                            await browser.page.wait_for_selector(
                                'text="Error: You already made a request to this faucet today. Try again tomorrow."',
                                timeout=1000,
                            )
                            logger.success(
                                f"{self.address} | Already used faucet today!"
                            )
                            await browser.stop()
                            return True
                        except:
                            continue

                except Exception as inner_err:
                    if "ElementHandle.click: Timeout 30000ms exceeded." in str(
                        inner_err
                    ):
                        logger.warning(
                            f"{self.address} | Capsolver unable to solve the captcha :( | Make sure you have correct API key in config.js"
                        )
                        await browser.stop()
                        return False

                    logger.warning(f"{self.address} | Error in retry loop: {inner_err}")
                    await asyncio.sleep(3)

            logger.warning(f"{self.address} | Faucet request timed out after 5 minutes")
            await browser.stop()
            return False

        except Exception as err:
            logger.error(f"{self.address} | Failed to request faucet: {err}")
            try:
                await browser.stop()
            except:
                pass
            return False

    async def buy_deform_nft(self) -> bool:
        try:
            amount = random.randint(
                self.config["buy_deform_nft"]["amount_to_buy"][0],
                self.config["buy_deform_nft"]["amount_to_buy"][1],
            )

            logger.info(f"{self.address} | Will try to buy {amount} Deform NFTs...")

            # Create separate web3 instance for Base network
            base_web3 = MyWeb3(
                random.choice(self.config["buy_deform_nft"]["base_network_rpc"]),
                self.client,
            )

            # Create contract instance
            contract_address = "0x5f8082f0AEd9FA8D0B67AdB6029A4BAC70eacb44"

            # Get gas estimates
            base_fee = await base_web3.web3.eth.gas_price
            max_priority_fee = await base_web3.get_priority_fee()
            max_fee = int(
                base_fee * 1.1 + max_priority_fee
            )  # Base fee + 10% + priority fee

            # Calculate total value (0.0004 ETH per NFT)
            total_value = base_web3.web3.to_wei(0.0004 * amount, "ether")

            # Create the transaction data with the specified amount
            data = (
                "0x08dc9f42"  # Method ID for mint(uint256,uint256,bytes)
                + "0000000000000000000000000000000000000000000000000000000000000001"  # _tokenId: 1
                + hex(amount)[2:].zfill(64)  # _amount: dynamic
                + "0000000000000000000000000000000000000000000000000000000000000060"  # offset for bytes
                + "0000000000000000000000000000000000000000000000000000000000000000"  # empty bytes
            )

            # Prepare transaction parameters
            transaction = {
                "chainId": 8453,  # Base network
                "from": self.address,
                "to": contract_address,
                "value": total_value,
                "data": data,
                "maxFeePerGas": max_fee,
                "maxPriorityFeePerGas": max_priority_fee,
                "type": 2,  # EIP-1559 transaction
                "nonce": await base_web3.web3.eth.get_transaction_count(self.address),
            }

            # Estimate gas
            gas = await base_web3.web3.eth.estimate_gas(transaction)
            transaction["gas"] = int(gas * 1.2)  # Add 20% buffer

            # Sign and send transaction
            signed_txn = base_web3.web3.eth.account.sign_transaction(
                transaction, self.private_key
            )
            tx_hash = await base_web3.web3.eth.send_raw_transaction(
                signed_txn.raw_transaction
            )

            logger.info(
                f"{self.address} | NFT mint transaction sent for {amount} NFTs: {constants.BASE_EXPLORER}0x{tx_hash.hex()}"
            )

            await asyncio.sleep(3)

            # Wait for transaction confirmation
            await base_web3.web3.eth.wait_for_transaction_receipt(tx_hash)
            logger.success(f"{self.address} | NFT mint transaction confirmed!")

            # result = await self.__verify_nft_mint(tx_hash.hex(), amount)
            # if not result:
            #     logger.error(
            #         f"{self.address} | NFT was minted but task was not verified!"
            #     )
            # else:
            #     logger.success(
            #         f"{self.address} | NFT was minted and task was verified!"
            #     )

            return True

        except Exception as err:
            logger.error(f"{self.address} | Error buy deform nft: {err}")
            return False

    async def collect_referral_code(self) -> str:
        try:
            if not await self._login_abstract():
                return False

            referral_code = await self.__get_user_info(
                collect_referral_code=True, log_user_info=True
            )

            return referral_code
        except Exception as err:
            logger.error(f"{self.address} | Error collect referral code: {err}")
            return ""

    async def show_user_info(self):
        try:
            if not await self._login_abstract():
                return False

            await self.__get_user_info(collect_referral_code=False, log_user_info=True)

            return True
        except Exception as err:
            logger.error(f"{self.address} | Error show user info: {err}")
            return False

    async def _login_abstract(self) -> bool:
        try:
            nonce = await self.__get_nonce()
            current_time = (
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            )

            signature_text = (
                "abstract.deform.cc wants you to sign in with your Ethereum account:\n"
                f"{self.address}\n\n"
                "By signing, you are proving you own this wallet and logging in. This does not initiate a transaction or cost any fees.\n\n"
                "URI: https://abstract.deform.cc\n"
                "Version: 1\n"
                "Chain ID: 1\n"
                f"Nonce: {nonce}\n"
                f"Issued At: {current_time}\n"
                "Resources:\n"
                "- https://privy.io"
            )

            signature = await self.web3.get_signature(signature_text, self.private_key)

            headers = {
                "accept": "application/json",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                "content-type": "application/json",
                "origin": "https://abstract.deform.cc",
                "priority": "u=1, i",
                "privy-app-id": constants.PRIVY_APP_ID,
                "referer": "https://abstract.deform.cc/",
                "sec-ch-ua": '"Google Chrome";v="120", "Chromium";v="120", "Not_A Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
            }

            json_data = {
                "message": signature_text,
                "signature": "0x" + signature,
                "chainId": "eip155:1",
                "walletClientType": "rabby_wallet",
                "connectorType": "injected",
            }

            response = await self.client.post(
                "https://auth.privy.io/api/v1/siwe/authenticate",
                headers=headers,
                json=json_data,
            )

            if response.status_code != 200:
                raise Exception(f"failed to login: {response.text}")

            data = response.json()

            self.login_tokens["bearer_token"] = data["token"]
            self.login_tokens["privy_access_token"] = data["privy_access_token"]
            self.login_tokens["refresh_token"] = data["refresh_token"]
            self.login_tokens["identity_token"] = data["identity_token"]

            self.client.headers.update(
                {"authorization": f"Bearer {self.login_tokens['bearer_token']}"}
            )

            if data["is_new_user"]:
                logger.success(f"{self.address} | Successfully registered new account!")
            else:
                logger.success(f"{self.address} | Successfully logged in!")

            headers = {
                "authorization": "",
                "content-type": "application/json",
                "origin": "https://abstract.deform.cc",
                "referer": "https://abstract.deform.cc/",
                "x-apollo-operation-name": "UserLogin",
            }

            json_data = {
                "operationName": "UserLogin",
                "variables": {
                    "data": {
                        "externalAuthToken": self.login_tokens["bearer_token"],
                    },
                },
                "query": "mutation UserLogin($data: UserLoginInput!) {\n  userLogin(data: $data)\n}",
            }

            response = await self.client.post(
                "https://api.deform.cc/", headers=headers, json=json_data
            )

            if response.status_code != 200:
                raise Exception(f"failed to UserLogin: {response.text}")

            self.login_tokens["userLogin"] = response.json()["data"]["userLogin"]

            if data["user"]["has_accepted_terms"]:
                logger.success(f"{self.address} | Terms already accepted!")
                return True
            else:
                result = await self._accept_terms()
                if result:
                    return True
                else:
                    logger.error(f"{self.address} | Failed to accept terms!")
                    return False

        except Exception as err:
            logger.error(f"{self.address} | Error login abstract: {err}")
            return False

    async def _accept_terms(self) -> bool:
        try:
            headers = {
                "accept": "application/json",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                "origin": "https://abstract.deform.cc",
                "priority": "u=1, i",
                "privy-app-id": constants.PRIVY_APP_ID,
                "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
            }

            json_data = {}

            response = await self.client.post(
                "https://auth.privy.io/api/v1/users/me/accept_terms",
                headers=headers,
                json=json_data,
            )

            if response.status_code != 200:
                raise Exception(f"failed to accept terms: {response.text}")

            if response.json()["has_accepted_terms"]:
                logger.success(f"{self.address} | Terms accepted!")
                return True
            else:
                logger.error(f"{self.address} | Failed to accept terms!")
                return False

        except Exception as err:
            logger.error(f"{self.address} | Error accept terms: {err}")
            return False

    async def _connect_twitter(self) -> bool:
        for retry in range(self.config["settings"]["tasks_attempts"]):
            try:
                state_code = "".join(
                    random.choice(string.ascii_letters + string.digits + "-_")
                    for _ in range(43)
                )

                characters = (
                    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_~."
                )
                code_verifier = "".join(secrets.choice(characters) for _ in range(43))

                input_bytes = code_verifier.encode("utf-8")
                sha256_hash = hashlib.sha256(input_bytes).digest()
                code_challenge = base64.b64encode(sha256_hash).decode("utf-8")

                code_challenge = (
                    code_challenge.replace("+", "-").replace("/", "_").replace("=", "")
                )

                headers = {
                    "accept": "application/json",
                    "authorization": f'Bearer {self.login_tokens["bearer_token"]}',
                    "content-type": "application/json",
                    "origin": "https://abstract.deform.cc",
                    "privy-app-id": constants.PRIVY_APP_ID,
                    "referer": "https://abstract.deform.cc/",
                }

                json_data = {
                    "provider": "twitter",
                    "redirect_to": "https://abstract.deform.cc/",
                    "code_challenge": code_challenge,
                    "state_code": state_code,
                }

                response = await self.client.post(
                    "https://auth.privy.io/api/v1/oauth/init",
                    headers=headers,
                    json=json_data,
                )

                # ++++++++++ #

                url = response.json()["url"]
                twitter_client = await create_twitter_client(
                    self.proxy, self.twitter_token
                )

                headers = {
                    "accept": "*/*",
                    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                    "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
                    "x-twitter-active-user": "yes",
                    "x-twitter-auth-type": "OAuth2Session",
                    "x-twitter-client-language": "en",
                }

                params = {
                    "client_id": "QzU1Y3VrM0xUaHdROWNJeGRZbkE6MTpjaQ",
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256",
                    "redirect_uri": "https://auth.privy.io/api/v1/oauth/callback",
                    "response_type": "code",
                    "scope": "users.read tweet.read offline.access",
                    "state": state_code,
                }

                response = await twitter_client.get(
                    "https://x.com/i/api/2/oauth2/authorize",
                    params=params,
                    headers=headers,
                )

                if "Could not authenticate you" in response.text:
                    raise Exception(
                        "twitter token is invalid. Please check your twitter token!"
                    )

                auth_code = response.json()["auth_code"]

                ct0 = twitter_client.headers.get("x-csrf-token")

                twitter_client.cookies.clear()
                twitter_client.cookies.update(
                    {
                        "auth_token": self.twitter_token,
                        "ct0": ct0,
                    }
                )
                headers = {
                    "x-twitter-auth-type": "OAuth2Session",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "content-type": "application/x-www-form-urlencoded",
                }

                data = {
                    "approval": "true",
                    "code": auth_code,
                }

                response = await twitter_client.post(
                    "https://x.com/i/api/2/oauth2/authorize", headers=headers, data=data
                )

                url = response.json()["redirect_uri"]

                # ++++++++++ #

                headers = {
                    "referer": "https://x.com/",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                }

                params = {
                    "state": state_code,
                    "code": auth_code,
                }

                response = await twitter_client.get(
                    "https://auth.privy.io/api/v1/oauth/callback",
                    params=params,
                    headers=headers,
                )

                url_data = unquote(str(response.url))

                privy_oauth_state = url_data.split("privy_oauth_state=")[1].split("&")[
                    0
                ]
                privy_oauth_code = url_data.split("privy_oauth_code=")[1].strip()

                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "origin": "https://abstract.deform.cc",
                    "privy-app-id": constants.PRIVY_APP_ID,
                    "privy-ca-id": "9acdc8c9-d8b2-44bb-bfde-928ae31c5b7b",
                    "privy-client": "react-auth:1.80.0-beta-20240821191745",
                    "referer": "https://abstract.deform.cc/",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                }

                json_data = {
                    "authorization_code": privy_oauth_code,
                    "state_code": privy_oauth_state,
                    "code_verifier": code_verifier,
                }
                response = await self.client.post(
                    "https://auth.privy.io/api/v1/oauth/link",
                    headers=headers,
                    json=json_data,
                )

                if response.status_code == 429:
                    logger.error(
                        f"{self.address} | Rate limit exceeded... Please try again later!"
                    )
                    return False

                if response.status_code != 200:
                    raise Exception(f"link request failed: {response.text}")
                else:
                    data = response.json()
                    for account in data["linked_accounts"]:
                        if account["type"] == "twitter_oauth":
                            logger.success(
                                f"{self.address} | Twitter account @{account['username']} connected!"
                            )
                            return True
                    logger.error(
                        f"{self.address} | No twitter account found in the response!"
                    )
                    return False

            except Exception as err:
                if "twitter token is invalid. Please check your twitter token!" in str(
                    err
                ):
                    logger.error(
                        f"{self.address} | Twitter token is invalid. Please check your twitter token!"
                    )
                    return False

                logger.error(
                    f"{self.address} | RETRY {retry+1}/{self.config['settings']['tasks_attempts']} | Error connect twitter: {err}"
                )
                random_pause = random.randint(
                    self.config["settings"]["pause_between_attempts"][0],
                    self.config["settings"]["pause_between_attempts"][1],
                )
                logger.info(f"{self.address} | Pausing for {random_pause} seconds...")
                await asyncio.sleep(random_pause)

        return False

    async def __do_task(self, task: dict):
        for retry in range(self.config["settings"]["tasks_attempts"]):
            try:
                task_name = task["title"]

                logger.info(f'{self.address} | Trying to do task "{task_name}"...')

                match task_name:
                    case "Campaign registration":
                        if self.config["settings"]["use_referral_code"]:
                            # Find and get referral code
                            async with self.config["async_lock"]:
                                with open(
                                    "data/referral_codes.txt", "r", encoding="utf-8"
                                ) as f:
                                    referral_lines = f.readlines()

                                # Get random number of required invites from config
                                required_invites = random.randint(
                                    self.config["settings"][
                                        "invites_per_referral_code"
                                    ][0],
                                    self.config["settings"][
                                        "invites_per_referral_code"
                                    ][1],
                                )

                                # Find first referral code with less than required invites
                                found_code = None
                                updated_lines = []

                                for line in referral_lines:
                                    address, ref_code, invites = line.strip().split(":")
                                    invites = int(invites)

                                    if not found_code and invites < required_invites:
                                        found_code = ref_code
                                        # We'll increment the counter only after successful registration

                                    updated_lines.append(
                                        f"{address}:{ref_code}:{invites}\n"
                                    )

                                if found_code:
                                    self.config["current_referral_code"] = found_code
                                    body = constants.get_verify_activity_json(
                                        found_code
                                    )
                                    logger.info(
                                        f"{self.address} | Using referral code: {found_code}"
                                    )

                                else:
                                    body = constants.get_verify_activity_json()
                        else:
                            body = constants.get_verify_activity_json()

                    case "Like our X post":
                        body = constants.LIKE_OUR_X_POST

                    case "Learn more about Abstract":
                        body = constants.LEARN_MORE_ABOUT_ABSTRACT

                    case "Like our X post about Panoramic Governance":
                        body = constants.LIKE_OUR_X_POST_ABOUT_PANORAMIC_GOVERNANCE

                    case "Repost our X post about Panoramic Governance":
                        body = constants.REPOST_OUR_X_POST_ABOUT_PANORAMIC_GOVERNANCE

                    case "Like our X post and learn about what's next for Abstract":
                        body = constants.LIKE_POST_AND_LEARN_NEXT_ABOUT_ABSTRACT

                    case "Like our X post about our October recap":
                        body = constants.LIKE_OUR_X_POST_ABOUT_OCTOBER_RECAP

                    case "Follow Abstract on X":
                        body = constants.FOLLOW_ABSTRACT_ON_X

                    case _:
                        logger.warning(f"{self.address} | Unknown task: {task_name}")
                        return False

                headers = {
                    "accept": "*/*",
                    "authorization": f'Bearer {self.login_tokens["userLogin"]}',
                    "content-type": "application/json",
                    "origin": "https://abstract.deform.cc",
                    "referer": "https://abstract.deform.cc/",
                    "x-apollo-operation-name": "VerifyActivity",
                }

                response = await self.client.post(
                    "https://api.deform.cc/", headers=headers, json=body
                )

                if "User has already completed the activity" in response.text:
                    logger.success(
                        f"{self.address} | Task {task_name} already completed!"
                    )
                    return True

                if response.status_code != 200:
                    raise Exception(f"{response.text}")
                else:
                    if (
                        response.json()["data"]["verifyActivity"]["record"]["status"]
                        == "COMPLETED"
                    ):
                        if task["title"] == "Campaign registration":
                            if (
                                self.config["settings"]["use_referral_code"]
                                and found_code
                            ):
                                async with self.config["async_lock"]:
                                    # Re-read the file to get the latest state
                                    with open(
                                        "data/referral_codes.txt", "r", encoding="utf-8"
                                    ) as f:
                                        referral_lines = f.readlines()

                                    updated_lines = []
                                    for line in referral_lines:
                                        address, ref_code, invites = line.strip().split(
                                            ":"
                                        )
                                        invites = int(invites)

                                        if ref_code == found_code:
                                            invites += 1

                                        updated_lines.append(
                                            f"{address}:{ref_code}:{invites}\n"
                                        )

                                    with open(
                                        "data/referral_codes.txt", "w", encoding="utf-8"
                                    ) as f:
                                        f.writelines(updated_lines)

                        logger.success(f"{self.address} | Task {task_name} completed!")
                        return True
                    else:
                        raise Exception(f"{response.text}")

            except Exception as err:
                logger.error(
                    f"{self.address} | RETRY {retry+1}/{self.config['settings']['tasks_attempts']} | Error do task {task['title']}: {err}"
                )
                random_pause = random.randint(
                    self.config["settings"]["pause_between_attempts"][0],
                    self.config["settings"]["pause_between_attempts"][1],
                )
                logger.info(f"{self.address} | Pausing for {random_pause} seconds...")
                await asyncio.sleep(random_pause)

        return False

    async def __get_user_info(
        self, collect_referral_code: bool = False, log_user_info: bool = False
    ):
        for retry in range(self.config["settings"]["tasks_attempts"]):
            try:
                response = await self.client.post(
                    "https://api.deform.cc/",
                    headers={
                        "x-apollo-operation-name": "UserMe",
                        "authorization": f"Bearer {self.login_tokens['userLogin']}",
                    },
                    json=constants.USER_INFO,
                )
                if response.status_code != 200:
                    raise Exception(f"{response.text}")

                if response.json().get("data"):
                    total_points = response.json()["data"]["userMe"]["campaignSpot"][
                        "points"
                    ]
                    referral_code = response.json()["data"]["userMe"]["campaignSpot"][
                        "referralCode"
                    ]

                    if log_user_info:
                        logger.info(
                            f"{self.address} | Total points: {total_points} | Referral code: {referral_code}"
                        )

                    if collect_referral_code:
                        return referral_code
                    else:
                        return response.json()

                else:
                    raise Exception(f"{response.text}")

            except Exception as err:
                logger.error(
                    f"{self.address} | RETRY {retry+1}/{self.config['settings']['tasks_attempts']} | Failed to get user info: {err}"
                )
                random_pause = random.randint(
                    self.config["settings"]["pause_between_attempts"][0],
                    self.config["settings"]["pause_between_attempts"][1],
                )
                logger.info(f"{self.address} | Pausing for {random_pause} seconds...")
                await asyncio.sleep(random_pause)

        return None

    async def __is_twitter_connected(self) -> bool:
        for retry in range(self.config["settings"]["tasks_attempts"]):
            try:
                response = await self.client.post(
                    "https://auth.privy.io/api/v1/sessions",
                    headers={
                        "authorization": f"Bearer {self.login_tokens['bearer_token']}",
                        "origin": "https://abstract.deform.cc",
                        "privy-app-id": constants.PRIVY_APP_ID,
                        "referer": "https://abstract.deform.cc/",
                    },
                    json={"refresh_token": self.login_tokens["refresh_token"]},
                )
                if response.status_code != 200:
                    raise Exception(f"{response.text}")

                for item in response.json()["user"]["linked_accounts"]:
                    if item["type"] == "twitter_oauth":
                        logger.success(
                            f"{self.address} | Twitter account @{item['username']} already connected!"
                        )
                        return True

                return False

            except Exception as err:
                logger.error(
                    f"{self.address} | RETRY {retry+1}/{self.config['settings']['tasks_attempts']} | Failed to get connected twitter info: {err}"
                )
                random_pause = random.randint(
                    self.config["settings"]["pause_between_attempts"][0],
                    self.config["settings"]["pause_between_attempts"][1],
                )
                logger.info(f"{self.address} | Pausing for {random_pause} seconds...")
                await asyncio.sleep(random_pause)

        raise Exception("Failed to get twitter account info")

    async def __get_tasks(self, tasks_only: bool = False):
        try:
            headers = {
                "authorization": f"Bearer {self.login_tokens['userLogin']}",
                "content-type": "application/json",
                "origin": "https://abstract.deform.cc",
                "referer": "https://abstract.deform.cc/",
                "x-apollo-operation-name": "Campaign",
            }

            response = await self.client.post(
                "https://api.deform.cc/", headers=headers, json=constants.ALL_TASKS_INFO
            )

            if response.status_code != 200:
                raise Exception(f"failed to get tasks: {response.text}")

            data = response.json()
            if tasks_only:
                return data["data"]["campaign"]["activities"]
            else:
                return data

        except Exception as err:
            logger.error(f"{self.address} | Error get tasks: {err}")
            return None

    async def __get_nonce(self) -> str:
        try:
            headers = {
                "accept": "application/json",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                "content-type": "application/json",
                "origin": "https://abstract.deform.cc",
                "priority": "u=1, i",
                "privy-app-id": constants.PRIVY_APP_ID,
                "referer": "https://abstract.deform.cc/",
                "sec-ch-ua": '"Google Chrome";v="120", "Chromium";v="120", "Not_A Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
            }

            json_data = {
                "address": self.address,
            }

            response = await self.client.post(
                "https://auth.privy.io/api/v1/siwe/init",
                headers=headers,
                json=json_data,
            )

            if response.status_code != 200:
                raise Exception(f"failed to get nonce: {response.text}")

            nonce = response.json()["nonce"]

            return nonce

        except Exception as err:
            logger.error(f"{self.address} | Error get nonce: {err}")
            raise err

    async def __verify_nft_mint(self, nft_tx_hash: str, num_mints: int) -> bool:
        for retry in range(self.config["settings"]["tasks_attempts"]):
            try:
                body = constants.get_verify_nft_mint_json(nft_tx_hash, num_mints)

                headers = {
                    "accept": "*/*",
                    "authorization": f'Bearer {self.login_tokens["userLogin"]}',
                    "content-type": "application/json",
                    "origin": "https://abstract.deform.cc",
                    "referer": "https://abstract.deform.cc/",
                    "x-apollo-operation-name": "VerifyActivity",
                }

                response = await self.client.post(
                    "https://api.deform.cc/", headers=headers, json=body
                )

                if response.status_code != 200:
                    raise Exception(f"{response.text}")

                return True

            except Exception as err:
                logger.error(
                    f"{self.address} | RETRY {retry+1}/{self.config['settings']['tasks_attempts']} | Error verify nft mint: {err}"
                )
                random_pause = random.randint(
                    self.config["settings"]["pause_between_attempts"][0],
                    self.config["settings"]["pause_between_attempts"][1],
                )
                logger.info(f"{self.address} | Pausing for {random_pause} seconds...")
                await asyncio.sleep(random_pause)

        return False
