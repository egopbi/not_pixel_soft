DELAYS = {
    "RELOGIN": [5, 7],  # delay after a login attempt
    'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
    'PLAY': [5, 15],   # delay between play in seconds
    'ERROR_PLAY': [5, 8],    # delay between errors in the game in seconds
    'CLAIM': [600, 1800],   # delay in seconds before claim points every 8 hours
    'GAME': [35, 37],  # delay after the start of the game
    'TASK_COMPLETE': [2, 3],  # delay after completed the task
    'TASK_ACTION': [5, 10]  # delay after start task
}

PROXY = {
    "USE_PROXY_FROM_DOTENV": False,  # True - if use proxy from dotenv, False - if don't use proxy
    "TYPE": {
        "TG": "http",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": "http"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
        }
}

# session folder (do not change)
WORKDIR = "sessions/"

# ADD YOUR OWN ABSOLUTE PATH!!!
SESSIONS_PATH = '/Users/...//not_pixel_my/sessions/'

# timeout in seconds for checking accounts on valid
TIMEOUT = 30