import random
import urllib3
import asyncio
import os
import sys

from telethon.sync import TelegramClient,functions
from urllib.parse import unquote
import aiohttp
from fake_useragent import UserAgent
from dotenv import load_dotenv

from utils.core import logger
import config

sys.path.append('/Users/egorpopov/softs/not_pixel_my/utils') 


load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

report_bug_text = "If you have done all the steps correctly and you think this is a bug, report it to github.com/aDarkDev with response. response: {}"
authenticate_error = "Please follow the steps correctly. Not authenticated."


async def get_web_app_data(client: TelegramClient): # lock):
    # async with lock:
        notcoin = await client.get_entity("notpixel")
        msg = await client(functions.messages.RequestWebViewRequest(notcoin,notcoin,platform="android",url="https://notpx.app/"))
        
        webappdata_global = msg.url.split('https://notpx.app/#tgWebAppData=')[1].replace("%3D","=").split('&tgWebAppVersion=')[0].replace("%26","&")
        user_data = webappdata_global.split("&user=")[1].split("&auth")[0]
        webappdata_global = webappdata_global.replace(user_data,unquote(user_data))
        return webappdata_global


class NotPx:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: dict, web_app_query: str):
        self.account = str(session_name) + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        self.name = self.account.split("/")[-1]
        
        # self.client = TelegramClient(
        #     session=session_name,
        #     api_id=os.getenv("API_ID"),
        #     api_hash=os.getenv("API_HASH"),
        #     proxy=proxy,
        # )

        self.web_app_query = web_app_query
        
        self.session_headers = {
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
            'User-Agent':UserAgent(os='linux').random}
        # print(f'\n\n\n>>>>>>>>>>>>>>>>>>>>>\n{session_name}\nSession headers: {self.session_headers}\n<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n\n')
        
    async def request(self, method, end_point, key_check, aiohttp_session: aiohttp.ClientSession, data=None, attempt=4):
        if attempt > 0:    
            try:
                if method == "get":
                    response = await aiohttp_session.get(f"https://notpx.app/api/v1{end_point}",timeout=5)
                    if response.status == 200:
                        text = await response.text()
                        if key_check in text:
                            json_response = await response.json()
                            return json_response
                        else:
                            raise Exception(report_bug_text.format(text))
                    else:
                        logger.error(f"Thread {self.thread} | {self.name} | ConnectionError {end_point}. Try to wait for 1 hour...")
                        raise Exception(authenticate_error)
                            
                            
                else:
                    response = await aiohttp_session.post(f"https://notpx.app/api/v1{end_point}",timeout=5,json=data)
                    if response.status == 200:
                        text = await response.text()
                        if key_check in text:
                            json_response = await response.json()
                            return json_response
                        else:
                            raise Exception(report_bug_text.format(text))
                    elif response.status >= 500:
                        await asyncio.sleep(5)
                        return await self.request(method,end_point,key_check,data)
                    else:
                        raise Exception(authenticate_error)
                
            except aiohttp.ClientConnectionError:
                logger.error(f"Thread {self.thread} | {self.account} | **Requester:** ConnectionError {end_point}. Sleeping for 5s...")
                attempt -= 1
                await asyncio.sleep(5)
                return await self.request(method, end_point, key_check, aiohttp_session, data, attempt=attempt)

            except urllib3.exceptions.NewConnectionError:
                logger.error(f"Thread {self.thread} | {self.account} | **Requester:** NewConnectionError {end_point}. Sleeping for 5s...")
                attempt -= 1
                await asyncio.sleep(5)
                return await self.request(method, end_point, key_check, aiohttp_session, data, attempt=attempt)
            
            except asyncio.TimeoutError:
                logger.error(f"Thread {self.thread} | {self.account} | **Requester:** TimeoutError {end_point}. Retrying in 7s...")
                attempt -= 1
                await asyncio.sleep(7)
                return await self.request(method, end_point, key_check, aiohttp_session, data, attempt=attempt)
        else:
            logger.error(f"Thread {self.thread} | {self.account} | **Requester:** Too many tries for request")
            return None


    async def claim_mining(self, aiohttp_session):
        try:
            claimed_count = (await self.request("get","/mining/claim","claimed", aiohttp_session))['claimed']
            return claimed_count
        except:
            return None

    async def accountStatus(self, aiohttp_session):
        return await self.request("get","/mining/status","speedPerSecond", aiohttp_session) # во всех сессиях выдает одно и то же значение

    async def autoPaintPixel(self, aiohttp_session):
        # making pixel randomly
        colors = [ "#FFFFFF" , "#000000" , "#00CC78" , "#BE0039" ]
        random_pixel = (random.randint(100,990) * 1000) + random.randint(100,990)
        data = {"pixelId":random_pixel,"newColor":random.choice(colors)}

        # Почему-то для разных сессий выдает одно значение 
        return (await self.request("post","/repaint/start","balance", aiohttp_session, data))['balance']
    
    async def paintPixel(self,x,y,hex_color, aiohttp_session):
        pixelformated = (y * 1000) + x + 1
        data = {"pixelId":pixelformated,"newColor":hex_color}

        return (await self.request("post","/repaint/start","balance",aiohttp_session, data))['balance']
    
    async def update_headers(self, client):
        # print('\n±±±±±±±±±±±±±±±±±±\nupdate headers starts\n±±±±±±±±±±±±±±±±±±±±±±\n')
        new_web_app_query = await get_web_app_data(client)
        # print('\n§§§§§§§§§§§§§§§§§§\nget new web app query\n§§§§§§§§§§§§§§§§§§§§§')
        self.session_headers['Authorization'] = f'initData {new_web_app_query}'
    
    # async def stats(self): # Недописано
    #     await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
    #     balance = (await self.request("get","/repaint/start","balance"))['balance']
    #     me = await self.client.get_me()
    #     phone_number = me.phone
    #     username = me.username
    #     proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'
    #     return [phone_number, username, balance, self.account, self.thread, proxy]