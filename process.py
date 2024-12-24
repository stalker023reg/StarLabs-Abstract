import asyncio
import random

from loguru import logger

import extra
from extra.logs import report_error, report_success
from extra.output import show_dev_info, show_logo
import model


async def start():
    async def launch_wrapper(index, proxy, private_key, twitter_token):
        async with semaphore:
            await account_flow(
                index + 1,
                proxy,
                private_key,
                twitter_token,
                config,
                lock,
            )

    show_logo()
    show_dev_info()
    config = extra.read_config()

    config["bridge_abi"] = extra.read_abi("extra/bridge_abi.json")
    config["async_lock"] = asyncio.Lock()

    proxies = extra.read_txt_file("proxies", "data/proxies.txt")
    private_keys = extra.read_txt_file("private keys", "data/private_keys.txt")

    # Читаем токены только если соответствующие задачи есть в конфиге
    twitter_tokens = (
        extra.read_txt_file("twitter tokens", "data/twitter_tokens.txt")
        if "main" in config["flow"]["tasks"]
        else [""] * len(private_keys)
    )

    threads = int(input("\nHow many threads do you want: "))
    print()

    if len(proxies) == 0:
        logger.error("No proxies found in data/proxies.txt")
        return

    proxies = [proxies[i % len(proxies)] for i in range(len(private_keys))]

    logger.info("Starting...")
    lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(value=threads)
    tasks = []
    for index, private_key in enumerate(private_keys):
        proxy = proxies[index % len(proxies)]
        tasks.append(
            asyncio.create_task(
                launch_wrapper(
                    index,
                    proxy,
                    private_key,
                    twitter_tokens[index],
                )
            )
        )

    await asyncio.gather(*tasks)

    logger.success("Saved accounts and private keys to a file.")


async def account_flow(
    account_index: int,
    proxy: str,
    private_key: str,
    twitter_token: str,
    config: dict,
    lock: asyncio.Lock,
):
    try:
        report = False

        instance = model.instance.Abstract(
            account_index, proxy, private_key, twitter_token, config
        )

        result = await wrapper(instance.initialize, config)
        if not result:
            report = True

        for task in config["flow"]["tasks"]:
            if task == "bridge":
                result = await wrapper(instance.bridge_eth, config)
                if not result:
                    report = True

                await random_sleep(config, task, instance.address)

            if task == "faucet":
                result = await wrapper(instance.faucet, config)
                if not result:
                    report = True

                await random_sleep(config, task, instance.address)

            if task == "main":
                result = await wrapper(instance.tasks, config)
                if not result:
                    report = True

                await random_sleep(config, task, instance.address)

            if task == "buy_deform_nft":
                result = await wrapper(instance.buy_deform_nft, config)
                if not result:
                    report = True

                await random_sleep(config, task, instance.address)

            if task == "collect_referral_code":
                result = await wrapper(instance.collect_referral_code, config)
                if not result:
                    report = True
                else:
                    async with lock:
                        with open(
                            "data/referral_codes.txt", "a", encoding="utf-8"
                        ) as f:
                            f.write(f"{instance.address}:{result}:0\n")

                await random_sleep(config, task, instance.address)

        if report:
            await report_error(lock, private_key, proxy, twitter_token)
        else:
            await report_success(lock, private_key, proxy, twitter_token)

        pause = random.randint(
            config["settings"]["random_pause_between_accounts"][0],
            config["settings"]["random_pause_between_accounts"][1],
        )
        logger.info(f"Sleeping for {pause} seconds before next account...")
        await asyncio.sleep(pause)

    except Exception as err:
        logger.error(f"{account_index} | Account flow failed: {err}")


async def wrapper(function, config: dict, *args, **kwargs):
    attempts = config["settings"]["attempts"]
    for attempt in range(attempts):
        result = await function(*args, **kwargs)
        if isinstance(result, tuple) and result and isinstance(result[0], bool):
            if result[0]:
                return result
        elif isinstance(result, bool):
            if result:
                return True

        if attempt < attempts - 1:  # Don't sleep after the last attempt
            pause = random.randint(
                config["settings"]["pause_between_attempts"][0],
                config["settings"]["pause_between_attempts"][1],
            )
            logger.info(
                f"Sleeping for {pause} seconds before next attempt {attempt+1}/{config['settings']['attempts']}..."
            )
            await asyncio.sleep(pause)

    return result


async def random_sleep(config: dict, task: str, address: str):
    pause = random.randint(
        config["settings"]["random_pause_between_actions"][0],
        config["settings"]["random_pause_between_actions"][1],
    )
    logger.info(f"{address} | Sleeping for {pause} seconds after {task}...")
    await asyncio.sleep(pause)
