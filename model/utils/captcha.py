import aiohttp
import asyncio
from loguru import logger


class Capsolver:
    def __init__(self, account_index: int, api_key: str):
        self.account_index = account_index
        self.api_key = api_key

    async def solve_recaptcha_v2(
        self, url: str, site_key: str, is_invisible: bool = False
    ) -> tuple[str, bool]:
        try:
            captcha_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ReCaptchaV2TaskProxyLess",
                    "websiteURL": url,
                    "websiteKey": site_key,
                    "isInvisible": is_invisible,
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.capsolver.com/createTask", json=captcha_data
                ) as resp:
                    if resp.status == 200:
                        logger.info(
                            f"{self.account_index} | Starting to solve reCAPTCHA v2..."
                        )
                        resp_json = await resp.json()
                        return await self.get_captcha_result(
                            session, resp_json["taskId"], "recaptcha_v2"
                        )
                    else:
                        resp_json = await resp.json()
                        logger.error(
                            f"{self.account_index} | Failed to send reCAPTCHA request: {resp_json['errorDescription']}"
                        )
                        return "", False

        except Exception as err:
            logger.error(
                f"{self.account_index} | Failed to send reCAPTCHA request: {err}"
            )
            return "", False

    async def solve_recaptcha_v3(
        self, url: str, site_key: str, page_action: str
    ) -> tuple[str, bool]:
        try:
            captcha_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ReCaptchaV3TaskProxyLess",
                    "websiteURL": url,
                    "websiteKey": site_key,
                    "pageAction": page_action,
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.capsolver.com/createTask", json=captcha_data
                ) as resp:
                    if resp.status == 200:
                        logger.info(
                            f"{self.account_index} | Starting to solve reCAPTCHA v3..."
                        )
                        resp_json = await resp.json()
                        return await self.get_captcha_result(
                            session, resp_json["taskId"], "recaptcha_v3"
                        )
                    else:
                        resp_json = await resp.json()
                        logger.error(
                            f"{self.account_index} | Failed to send reCAPTCHA v3 request: {resp_json['errorDescription']}"
                        )
                        return "", False

        except Exception as err:
            logger.error(
                f"{self.account_index} | Failed to send reCAPTCHA v3 request: {err}"
            )
            return "", False

    # returns gRecaptchaResponse, resp_key and success status (False if something failed)
    async def solve_cloudflare(self, url: str, site_key: str) -> tuple[str, bool]:
        try:
            captcha_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "AntiTurnstileTaskProxyLess",
                    "websiteURL": url,
                    "websiteKey": site_key,
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.capsolver.com/createTask", json=captcha_data
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"{self.account_index} | Starting to solve CF...")
                        resp_json = await resp.json()
                        return await self.get_captcha_result(
                            session, resp_json["taskId"], "cloudflare"
                        )
                    else:
                        resp_json = await resp.json()
                        logger.error(
                            f"{self.account_index} | Failed to send CF request: {resp_json['errorDescription']}"
                        )
                        return "", False

        except Exception as err:
            logger.error(
                f"{self.account_index} | Failed to send CF request to 2captcha: {err}"
            )
            return "", False

    async def get_captcha_result(
        self, session: aiohttp.ClientSession, task_id: str, captcha_type: str
    ) -> tuple[str, bool]:
        for i in range(30):
            try:
                async with session.post(
                    "https://api.capsolver.com/getTaskResult",
                    json={"clientKey": self.api_key, "taskId": task_id},
                ) as resp:
                    if resp.status == 200:
                        resp_json = await resp.json()
                        print(resp_json)
                        if resp_json["errorId"] != 0:
                            logger.error(
                                f"{self.account_index} | {captcha_type.upper()} failed!"
                            )
                            return "", False

                        elif resp_json["status"] == "ready":
                            logger.success(
                                f"{self.account_index} | {captcha_type.upper()} solved!"
                            )

                            # Get appropriate response field based on captcha type
                            if captcha_type in ["recaptcha_v2", "recaptcha_v3"]:
                                response = resp_json["solution"]["gRecaptchaResponse"]
                            else:  # cloudflare
                                response = resp_json["solution"]["token"]

                            return response, True

            except Exception as err:
                logger.error(
                    f"{self.account_index} | Failed to get {captcha_type.upper()} solution: {err}"
                )
                return "", False

            # sleep between result requests
            await asyncio.sleep(7)

        logger.error(
            f"{self.account_index} | Failed to get {captcha_type.upper()} solution"
        )
        return "", False


class TwoCaptcha:
    def __init__(self, account_index: int, api_key: str):
        self.account_index = account_index
        self.api_key = api_key
        self.base_url = "http://2captcha.com"

    async def solve_recaptcha_v2(
        self,
        url: str,
        site_key: str,
        is_invisible: bool = False,
        data_s: str = None,
        cookies: str = None,
        user_agent: str = None,
    ) -> tuple[str, bool]:
        try:
            # Create task
            params = {
                "key": self.api_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": url,
                "json": 1,
            }

            # Add optional parameters
            if is_invisible:
                params["invisible"] = 1
            if data_s:
                params["data-s"] = data_s
            if cookies:
                params["cookies"] = cookies
            if user_agent:
                params["userAgent"] = user_agent

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/in.php", params=params
                ) as resp:
                    if resp.status == 200:
                        resp_json = await resp.json()

                        if resp_json.get("status") == 1:
                            logger.info(
                                f"{self.account_index} | Starting to solve reCAPTCHA v2{'(invisible)' if is_invisible else ''}..."
                            )
                            return await self.get_captcha_result(
                                session, resp_json["request"]
                            )
                        else:
                            logger.error(
                                f"{self.account_index} | Failed to create reCAPTCHA v2 task: {resp_json.get('error_text')}"
                            )
                            return "", False
                    else:
                        logger.error(
                            f"{self.account_index} | Failed to create reCAPTCHA v2 task: HTTP {resp.status}"
                        )
                        return "", False

        except Exception as err:
            logger.error(
                f"{self.account_index} | Failed to create reCAPTCHA v2 task: {err}"
            )
            return "", False

    async def solve_recaptcha_v3(
        self,
        url: str,
        site_key: str,
        page_action: str = "verify",
        min_score: float = 0.3,
    ) -> tuple[str, bool]:
        try:
            # Create task
            params = {
                "key": self.api_key,
                "method": "userrecaptcha",
                "version": "v3",
                "action": page_action,
                "min_score": min_score,
                "googlekey": site_key,
                "pageurl": url,
                "json": 1,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/in.php", params=params
                ) as resp:
                    if resp.status == 200:
                        resp_json = await resp.json()

                        if resp_json.get("status") == 1:
                            logger.info(
                                f"{self.account_index} | Starting to solve reCAPTCHA v3..."
                            )
                            return await self.get_captcha_result(
                                session, resp_json["request"]
                            )
                        else:
                            logger.error(
                                f"{self.account_index} | Failed to create reCAPTCHA v3 task: {resp_json.get('error_text')}"
                            )
                            return "", False
                    else:
                        logger.error(
                            f"{self.account_index} | Failed to create reCAPTCHA v3 task: HTTP {resp.status}"
                        )
                        return "", False

        except Exception as err:
            logger.error(
                f"{self.account_index} | Failed to create reCAPTCHA v3 task: {err}"
            )
            return "", False

    async def get_captcha_result(
        self, session: aiohttp.ClientSession, task_id: str
    ) -> tuple[str, bool]:
        params = {"key": self.api_key, "action": "get", "id": task_id, "json": 1}

        for i in range(30):  # 30 attempts with 5 second delay = 150 seconds max
            try:
                async with session.get(
                    f"{self.base_url}/res.php", params=params
                ) as resp:
                    if resp.status == 200:
                        resp_json = await resp.json()

                        if resp_json.get("status") == 1:
                            logger.success(
                                f"{self.account_index} | reCAPTCHA v3 solved!"
                            )
                            return resp_json["request"], True

                        elif resp_json.get("request") == "CAPCHA_NOT_READY":
                            await asyncio.sleep(5)
                            continue

                        else:
                            logger.error(
                                f"{self.account_index} | Failed to get solution: {resp_json.get('error_text')}"
                            )
                            return "", False

            except Exception as err:
                logger.error(f"{self.account_index} | Failed to get solution: {err}")
                return "", False

        logger.error(f"{self.account_index} | Timeout waiting for solution")
        return "", False

    async def report_result(self, task_id: str, success: bool) -> bool:
        try:
            params = {
                "key": self.api_key,
                "action": "reportgood" if success else "reportbad",
                "id": task_id,
                "json": 1,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/res.php", params=params
                ) as resp:
                    if resp.status == 200:
                        resp_json = await resp.json()
                        if resp_json.get("status") == 1:
                            logger.info(
                                f"{self.account_index} | Successfully reported {'good' if success else 'bad'} result"
                            )
                            return True

                    logger.error(f"{self.account_index} | Failed to report result")
                    return False

        except Exception as err:
            logger.error(f"{self.account_index} | Failed to report result: {err}")
            return False
