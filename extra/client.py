from noble_tls import Session, Client

from extra.constants import USER_AGENT


async def create_client(proxy: str) -> Session:
    session = Session(client=Client.CHROME_120)
    session.random_tls_extension_order = True

    if proxy:
        session.proxies.update({
            "http": "http://" + proxy,
            "https": "http://" + proxy,
        })

    session.timeout_seconds = 30

    session.headers.update(HEADERS)

    return session

HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5',
    'content-type': 'application/json',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Google Chrome";v="120", "Chromium";v="120", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': USER_AGENT,
}


import secrets

async def create_twitter_client(proxy: str, auth_token: str) -> Session:
    session = Session(client=Client.CHROME_120)
    session.random_tls_extension_order = True

    if proxy:
        session.proxies.update({
            "http": "http://" + proxy,
            "https": "http://" + proxy,
        })

    session.timeout_seconds = 30

    generated_csrf_token = secrets.token_hex(16)
    guest_token = await request_guest_token(session, generated_csrf_token)

    cookies = {"ct0": generated_csrf_token, "auth_token": auth_token}
    headers = {"x-csrf-token": generated_csrf_token}

    session.headers.update(headers)
    session.cookies.update(cookies)

    session.headers["x-csrf-token"] = generated_csrf_token

    session.headers = get_headers(session)

    return session


def get_headers(session: Session, **kwargs) -> dict:
    """
    Get the headers required for authenticated requests
    """
    cookies = session.cookies

    headers = kwargs | {
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        # "cookie": "; ".join(f"{k}={v}" for k, v in cookies.items()),
        "referer": "https://x.com/",
        "user-agent": USER_AGENT,
        "x-csrf-token": cookies.get("ct0", ""),
        # "x-guest-token": cookies.get("guest_token", ""),
        "x-twitter-auth-type": "OAuth2Session" if cookies.get("auth_token") else "",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "en",
    }
    return dict(sorted({k.lower(): v for k, v in headers.items()}.items()))


async def request_ct0(session) -> str:
    url = "https://x.com/i/api/2/oauth2/authorize"
    r = await session.get(url, allow_redirects=True)

    if "ct0" in r.cookies:
        return r.cookies.get("ct0")
    else:
        raise Exception("Make sure you are using correct cookies.")


async def request_guest_token(
        session: Session, csrf_token: str = None
) -> str:
    if not (csrf_token, session.cookies.get("ct0", "")):
        raise Exception("Failed to get guest token.")

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "x-csrf-token": (
            csrf_token if csrf_token else session.cookies.get("ct0")
        ),
    }
    r = await session.post(
        f"https://api.twitter.com/1.1/guest/activate.json",
        headers=headers,
        allow_redirects=True,
    )

    _data = r.json()
    return _data["guest_token"]


