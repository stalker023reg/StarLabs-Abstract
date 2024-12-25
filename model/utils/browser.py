import os
import tempfile
import uuid
import random
from typing import List, Dict
from patchright.async_api import async_playwright
from loguru import logger


def get_random_user_agent() -> str:
    chrome_versions = [
        "110.0.0.0",
        "111.0.0.0",
        "112.0.0.0",
        "113.0.0.0",
        "114.0.0.0",
        "115.0.0.0",
        "116.0.0.0",
        "117.0.0.0",
        "118.0.0.0",
        "119.0.0.0",
        "120.0.0.0",
    ]

    platforms = [
        ("Windows NT 10.0; Win64; x64", "Windows"),
        ("Macintosh; Intel Mac OS X 10_15_7", "macOS"),
        ("X11; Linux x86_64", "Linux"),
    ]

    platform, os_name = random.choice(platforms)
    chrome_version = random.choice(chrome_versions)

    return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"


def get_random_viewport() -> Dict[str, int]:
    resolutions = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 720},
    ]
    return random.choice(resolutions)


def get_random_timezone() -> str:
    timezones = [
        "America/New_York",
        "America/Chicago",
        "America/Los_Angeles",
        "America/Phoenix",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Asia/Tokyo",
        "Asia/Singapore",
        "Australia/Sydney",
    ]
    return random.choice(timezones)


def get_random_launch_args(capsolver_path: str) -> List[str]:
    base_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--password-store=basic",
        "--use-mock-keychain",
        "--disable-software-rasterizer",
        "--disable-gpu-sandbox",
        "--no-default-browser-check",
        "--allow-running-insecure-content",
    ]

    optional_args = [
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-site-isolation-trials",
        "--disable-setuid-sandbox",
        "--ignore-certificate-errors",
        "--disable-accelerated-2d-canvas",
        "--disable-bundled-ppapi-flash",
        "--disable-logging",
        "--disable-notifications",
    ]

    # Randomly select 2-4 optional arguments
    selected_optional = random.sample(optional_args, random.randint(2, 4))

    # Add extension-specific arguments
    extension_args = [
        f"--disable-extensions-except={capsolver_path}",
        f"--load-extension={capsolver_path}",
        "--lang=en-US",
    ]

    return base_args + selected_optional + extension_args


class CreateBrowserInstance:
    def __init__(self, proxy_string: str = ""):
        self.proxy_string = proxy_string
        self.playwright = None
        self.context = None
        self.page = None
        self.is_running = False

        # Extension paths
        base_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.capsolver_path = os.path.join(base_path, "extra", "capsolver_extension")

        self.session_id = str(uuid.uuid4())
        self.user_data_dir = os.path.join(
            tempfile.gettempdir(), f"chrome_profile_{self.session_id}"
        )

    async def start(self):
        """Запуск и инициализация браузера"""
        try:
            if self.is_running:
                logger.warning("Browser is already running")
                return True

            self.playwright = await async_playwright().start()

            # Get random settings
            user_agent = get_random_user_agent()
            viewport = get_random_viewport()
            timezone = get_random_timezone()
            launch_args = get_random_launch_args(self.capsolver_path)

            # Add window size to launch args based on viewport
            launch_args.append(
                f"--window-size={viewport['width']},{viewport['height']}"
            )

            context_settings = {
                "channel": "chrome",
                "no_viewport": True,
                "user_agent": user_agent,
                "locale": random.choice(["en-US", "en-GB", "en-CA"]),
                "timezone_id": timezone,
                "ignore_https_errors": True,
                "bypass_csp": True,
                "java_script_enabled": True,
                "accept_downloads": True,
                "headless": False,
                "args": launch_args,
                "chromium_sandbox": False,
                "viewport": viewport,
            }

            if self.proxy_string:
                proxy_config = self.parse_proxy(self.proxy_string)
                if proxy_config:
                    context_settings["proxy"] = proxy_config

            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir, timeout=60000, **context_settings
            )

            self.page = await self.context.new_page()

            await self.page.add_init_script(
                """
                (() => {
                    delete Object.getPrototypeOf(navigator).webdriver;
                    
                    window.chrome = {
                        app: {
                            InstallState: {
                                DISABLED: 'DISABLED',
                                INSTALLED: 'INSTALLED',
                                NOT_INSTALLED: 'NOT_INSTALLED'
                            },
                            RunningState: {
                                CANNOT_RUN: 'CANNOT_RUN',
                                READY_TO_RUN: 'READY_TO_RUN',
                                RUNNING: 'RUNNING'
                            },
                            getDetails: function() {},
                            getIsInstalled: function() {},
                            installState: function() {
                                return 'INSTALLED';
                            },
                            isInstalled: true,
                            runningState: function() {
                                return 'RUNNING';
                            }
                        },
                        runtime: {
                            OnInstalledReason: {
                                CHROME_UPDATE: 'chrome_update',
                                INSTALL: 'install',
                                SHARED_MODULE_UPDATE: 'shared_module_update',
                                UPDATE: 'update'
                            },
                            OnRestartRequiredReason: {
                                APP_UPDATE: 'app_update',
                                OS_UPDATE: 'os_update',
                                PERIODIC: 'periodic'
                            },
                            PlatformArch: {
                                ARM: 'arm',
                                ARM64: 'arm64',
                                MIPS: 'mips',
                                MIPS64: 'mips64',
                                X86_32: 'x86-32',
                                X86_64: 'x86-64'
                            },
                            PlatformNaclArch: {
                                ARM: 'arm',
                                MIPS: 'mips',
                                MIPS64: 'mips64',
                                X86_32: 'x86-32',
                                X86_64: 'x86-64'
                            },
                            PlatformOs: {
                                ANDROID: 'android',
                                CROS: 'cros',
                                LINUX: 'linux',
                                MAC: 'mac',
                                OPENBSD: 'openbsd',
                                WIN: 'win'
                            },
                            RequestUpdateCheckStatus: {
                                NO_UPDATE: 'no_update',
                                THROTTLED: 'throttled',
                                UPDATE_AVAILABLE: 'update_available'
                            }
                        }
                    };
                    
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [{
                            0: {
                                type: "application/x-google-chrome-pdf",
                                suffixes: "pdf",
                                description: "Portable Document Format",
                                enabledPlugin: true
                            },
                            name: "Chrome PDF Plugin",
                            filename: "internal-pdf-viewer",
                            description: "Portable Document Format"
                        }]
                    });
                    
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    window.cdc_adoQpoasnfa76pfcZLmcfl_Array = undefined;
                    window.cdc_adoQpoasnfa76pfcZLmcfl_Promise = undefined;
                    window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol = undefined;
                })();
            """
            )

            await self.page.set_extra_http_headers(
                {
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "sec-ch-ua": f'"Chromium";v="{random.randint(110, 120)}", "Not(A:Brand";v="{random.randint(8, 24)}", "Google Chrome";v="{random.randint(110, 120)}"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": f'"{viewport["platform"] if "platform" in viewport else "Windows"}"',
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": user_agent,
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                    "sec-fetch-user": "?1",
                    "Connection": "keep-alive",
                }
            )

            self.is_running = True
            return True
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            await self.stop()
            return False

    async def stop(self):
        """Корректное закрытие всех ресурсов"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
            self.is_running = False
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
            raise

    @staticmethod
    def parse_proxy(proxy_string: str) -> dict:
        """Парсинг строки прокси"""
        try:
            if "@" in proxy_string:
                auth, proxy = proxy_string.split("@")
                username, password = auth.split(":")
                host, port = proxy.split(":")
                return {
                    "server": f"http://{host}:{port}",
                    "username": username,
                    "password": password,
                }
            else:
                host, port = proxy_string.split(":")
                return {"server": f"http://{host}:{port}"}
        except Exception as e:
            logger.error(f"Error parsing proxy string: {e}")
            return {}

    async def navigate_to(self, url: str):
        """Навигация по URL"""
        if not self.is_running:
            raise RuntimeError("Browser is not running")

        try:
            await self.page.goto(url, wait_until="networkidle")
            logger.info(f"Successfully navigated to {url}")
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            raise
