import random
import urllib3
import asyncio
import os

from telethon.sync import TelegramClient,functions
from urllib.parse import unquote
import aiohttp
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector
from dotenv import load_dotenv

from utils.core import logger
from utils.core.telegram import parse_proxy
import config



load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

report_bug_text = "If you have done all the steps correctly and you think this is a bug, report it to github.com/aDarkDev with response. response: {}"
authenticate_error = "Please follow the steps correctly. Not authenticated."

def retry_async(max_retries=2):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            thread, account = args[0].thread, args[0].account
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    logger.error(f"Thread {thread} | {account} | **Error:** {e}. Retrying {retries}/{max_retries}...")
                    await asyncio.sleep(10)
                    if retries >= max_retries:
                        break
        return wrapper
    return decorator
    
client = TelegramClient("NotPx_Auto",api_id,api_hash).start()

async def get_web_app_data():
    notcoin = await client.get_entity("notpixel")
    msg = await client(functions.messages.RequestWebViewRequest(notcoin,notcoin,platform="android",url="https://notpx.app/"))
    
    webappdata_global = msg.url.split('https://notpx.app/#tgWebAppData=')[1].replace("%3D","=").split('&tgWebAppVersion=')[0].replace("%26","&")
    user_data = webappdata_global.split("&user=")[1].split("&auth")[0]
    webappdata_global = webappdata_global.replace(user_data,unquote(user_data))
    return webappdata_global


class NotPx:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None], web_app_query: str):
        self.account = str(session_name) + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)
        self.web_app_query = web_app_query

        if proxy:
            proxy = parse_proxy(proxy)

        self.client = TelegramClient(
            session=session_name,
            api_id=os.getenv("API_ID"),
            api_hash=os.getenv("API_HASH"),
            proxy=proxy,
        )
        # web_app_query = get_web_app_data()
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': f'initData {self.web_app_query}',
            'Priority': 'u=1, i',
            'Referer': 'https://notpx.app/',
            'Sec-Ch-Ua': 'Chromium;v=119, Not?A_Brand;v=24',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': 'Linux',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': UserAgent(browsers='chrome', os='linux').random}
        print(f'\n\n\n>>>>>>>>>>>>>>>>>>>>>\n{headers}\n<<<<<<<<<<>>>>>>>>><<<<<<\n\n\n')
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector, timeout=aiohttp.ClientTimeout(120))
        

    async def request(self,method,end_point,key_check,data=None):
        try:
            if method == "get":
                response = await self.session.get(f"https://notpx.app/api/v1{end_point}",timeout=5)
                if response.status == 200:
                    text = await response.text()
                    if key_check in text:
                        json_response = await response.json()
                        return json_response
                    else:
                        raise Exception(report_bug_text.format(text))
                else:
                    raise Exception(authenticate_error)
            else:
                response = await self.session.post(f"https://notpx.app/api/v1{end_point}",timeout=5,json=data)
                if response.status == 200:
                    text = await response.text()
                    if key_check in text:
                        json_response = await response.json()
                        return json_response
                    else:
                        raise Exception(report_bug_text.format(text))
                elif response.status_code >= 500:
                    await asyncio.sleep(5)
                    return await self.request(method,end_point,key_check,data)
                else:
                    raise Exception(authenticate_error)
        
        except aiohttp.ClientConnectionError:
            logger.error(f"Thread {self.thread} | {self.account} | **Requester:** ConnectionError {end_point}. Sleeping for 5s...")
            asyncio.sleep(5)

        except urllib3.exceptions.NewConnectionError:
            logger.error(f"Thread {self.thread} | {self.account} | **Requester:** NewConnectionError {end_point}. Sleeping for 5s...")
            asyncio.sleep(5)

    
    async def claim_mining(self):
        return (await self.request("get","/mining/claim","claimed"))['claimed']

    async def accountStatus(self):
        return await self.request("get","/mining/status","speedPerSecond")

    async def autoPaintPixel(self):
        # making pixel randomly
        colors = [ "#FFFFFF" , "#000000" , "#00CC78" , "#BE0039" ]
        random_pixel = (random.randint(100,990) * 1000) + random.randint(100,990)
        data = {"pixelId":random_pixel,"newColor":random.choice(colors)}

        return (await self.request("post","/repaint/start","balance",data))['balance']
    
    async def paintPixel(self,x,y,hex_color):
        pixelformated = (y * 1000) + x + 1
        data = {"pixelId":pixelformated,"newColor":hex_color}

        return (await self.request("post","/repaint/start","balance",data))['balance']
    
    async def stats(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        balance = (await self.request("get","/repaint/start","balance"))['balance']
        me = await self.client.get_me()
        phone_number = me.phone
        username = me.username
        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'
        return [phone_number, username, balance, self.account, self.thread, proxy]