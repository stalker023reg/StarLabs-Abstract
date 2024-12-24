import asyncio
import functools
import random

from loguru import logger


async def random_pause(start, end):
    await asyncio.sleep(random.randint(start, end))


def retry(attempts, log_indicator_func=lambda _: "-"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            log_indicator = log_indicator_func(self)
            for attempt in range(1, attempts + 1):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    await asyncio.sleep(1)
                    if attempt == attempts:
                        logger.error(f"{log_indicator} | All attempts failed. Error: {str(e)}")
                        raise

        return wrapper

    return decorator
