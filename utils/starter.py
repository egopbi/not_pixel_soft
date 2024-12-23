import random 
import asyncio
import urllib3
import pandas as pd
import aiohttp

import pathlib
from aiohttp_socks import ProxyConnector
from telethon.sync import TelegramClient

import config
from utils.core.telegram import Accounts
from utils.core import logger
from utils.notpixel import NotPx


async def autopainter(thread: int, session_name: str, NotPxClient: NotPx, client: TelegramClient):
    await asyncio.sleep(random.randint(20,1850))
    logger.info(f"Thread {thread} | {session_name} | **Painter:** Auto painting started!")
    while True:
        await NotPxClient.update_headers(client=client)
        async with aiohttp.TCPConnector(verify_ssl=False) as connector:
            async with aiohttp.ClientSession(
                headers=NotPxClient.session_headers,
                trust_env=True,
                connector=connector,
                timeout=aiohttp.ClientTimeout(300)
                ) as aiohttp_session:
                try:
                    await asyncio.sleep(random.randint(2, 4))
                    acc_data = await NotPxClient.accountStatus(aiohttp_session)
                    if not acc_data:
                        logger.error(f"Thread {thread} | {session_name} | **Painter:** account_data was not recieved")
                        await asyncio.sleep(5)
                        continue
                    else:
                        logger.info(f"Thread {thread} | {session_name} | **Painter:** account_data was recieved")
                        charges = acc_data['charges']
                    try:
                        if charges > 0:    
                            for _ in range(charges):
                                balance = await NotPxClient.autoPaintPixel(aiohttp_session)
                                logger.success(f"Thread {thread} | {session_name} | **Painter:** 1 Pixel painted successfully! \
User new balance: {balance}")
                                t = random.randint(1,4)
                                logger.info(f"Thread {thread} | {session_name} | **Painter antidetect:** Sleeping for {t} seconds...")
                                await asyncio.sleep(t)
#                             x = random.randint(181, 244)
#                             y = random.randint(170, 229)
#                             for i in range(charges):
#                                 if i % 2 == 0:
#                                     balance = await NotPxClient.paint_first_pixel(x=x, y=y, aiohttp_session=aiohttp_session)
#                                     logger.success(f"Thread {thread} | {session_name} | **Painter:** 1 Pixel painted successfully on ({x,y})! \
# User new balance: {balance}")
#                                 else:
#                                     balance = await NotPxClient.repaint_first_pixel(x=x, y=y, aiohttp_session=aiohttp_session)
#                                     logger.success(f"Thread {thread} | {session_name} | **Painter:** 1 Pixel repainted successfully on ({x,y})! \
# User new balance: {balance}")
#                                     x = x + random.randint(-1, 1)
#                                     y = y + random.randint(-1, 1)
                                
#                                 t = random.randint(1,3)
#                                 logger.info(f"Thread {thread} | {session_name} | **Painter antidetect:** Sleeping for {t} seconds...")
#                                 await asyncio.sleep(t)
                    except:
                        logger.error(f"Thread {thread} | {session_name} | **Painter:** RequestError. Sleeping for 20s...")
                        await asyncio.sleep(20)
                                

                except aiohttp.ClientConnectionError:
                    logger.error(f"Thread {thread} | {session_name} | **Painter:** ConnectionError. Sleeping for 5s...")
                    await asyncio.sleep(5)

                except urllib3.exceptions.NewConnectionError:
                    logger.error(f"Thread {thread} | {session_name} | **Painter:** NewConnectionError. Sleeping for 5s...")
                    await asyncio.sleep(5)

                except asyncio.TimeoutError:
                    er = random.randint(60,120)
                    logger.error(f"Thread {thread} | {session_name} | **Painter:** TimeOutError. Sleeping for {er}s...")
                    await asyncio.sleep(er)

        d = random.randint(2420, 6000) 
        logger.info(f"Thread {thread} | {session_name} | **Painter:** No charge avaliable. Sleeping for {d} seconds...")
        await asyncio.sleep(d)


async def mine_claimer(thread: int, session_name: str, NotPxClient: NotPx, client: TelegramClient):
    await asyncio.sleep(random.randint(600,1800))
    logger.info(f"Thread {thread} | {session_name} | **Miner:** Mine claiming started!") 
    while True:
        await NotPxClient.update_headers(client=client)
        async with aiohttp.TCPConnector(verify_ssl=False) as connector:
            async with aiohttp.ClientSession(
                headers=NotPxClient.session_headers,
                trust_env=True,
                connector=connector,
                timeout=aiohttp.ClientTimeout(300)
                ) as aiohttp_session:
                
                try:
                    await asyncio.sleep(random.randint(2, 4))
                    acc_data = await NotPxClient.accountStatus(aiohttp_session)
                
                    if not acc_data:
                        logger.error(f"Thread {thread} | {session_name} | **Miner:** account_data was not recieved")
                        await asyncio.sleep(5)
                        continue
                    else:
                        logger.info(f"Thread {thread} | {session_name} | **Miner:** account_data was recieved")
                        
                        claimed_count = await NotPxClient.claim_mining(aiohttp_session)
                        if claimed_count is None:
                            logger.info(f"Thread {thread} | {session_name} | **Miner:** Error request. Sleeping for 1 hour...")
                            await asyncio.sleep(3600)
                        else:
                            claimed_count = round(claimed_count,2)
                            logger.success(f"Thread {thread} | {session_name} | **Miner:** {claimed_count} NotPx token was claimed.")
                
                except aiohttp.ClientConnectionError:
                    logger.error(f"Thread {thread} | {session_name} | **Painter:** ConnectionError. Sleeping for 5s...")
                    await asyncio.sleep(5)

                except urllib3.exceptions.NewConnectionError:
                    logger.error(f"Thread {thread} | {session_name} | **Painter:** NewConnectionError. Sleeping for 5s...")
                    await asyncio.sleep(5)

                except asyncio.TimeoutError:
                    er = random.randint(60,120)
                    logger.error(f"Thread {thread} | {session_name} | **Painter:** TimeOutError. Sleeping for {er}s...")
                    await asyncio.sleep(er)

        sleep_time = random.randint(5000,17000)
        logger.info(f"Thread {thread} | {session_name} | **Miner:** Sleeping for {sleep_time} seconds...")
        await asyncio.sleep(sleep_time)


async def start(thread: int, session_name: str, phone_number: str, proxy: dict, web_app_query: str, client: TelegramClient):
    await asyncio.sleep(random.randint(1,10))
    NotPxClient = NotPx(
        thread=thread,
        session_name=pathlib.Path(config.SESSIONS_PATH, session_name),
        phone_number=phone_number,
        proxy=proxy,
        web_app_query=web_app_query,
        )
    session_name = session_name + '.session'

# Used when need to change the template
    """ 
    async with aiohttp.TCPConnector(verify_ssl=False) as connector:
            async with aiohttp.ClientSession(
                headers=NotPxClient.session_headers,
                trust_env=True,
                connector=connector,
                timeout=aiohttp.ClientTimeout(300)
                ) as aiohttp_session:
    
                try:
                    await NotPxClient.subscribe_template(
                        aiohttp_session=aiohttp_session, 
                        template_address="/image/template/subscribe/2087443613"
                        )
                except:
                    logger.error("Can't subscribe to template")

"""
    await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
    await asyncio.gather(
    autopainter(thread=thread, session_name=session_name, NotPxClient=NotPxClient, client=client),
    mine_claimer(thread=thread, session_name=session_name, NotPxClient=NotPxClient, client=client)
    )


           
# Not working yet, start change with webappquery
"""
async def stats():
    accounts = await Accounts().get_accounts()
    # web_app_query = await get_web_app_data()
    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(NotPx(
            session_name=pathlib.Path(config.SESSIONS_PATH, session_name), 
            phone_number=phone_number, 
            thread=thread, 
            proxy=proxy,
            web_app_query=web_app_query,
            ).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Phone number', 'Name', 'Points', 'Session', 'Thread', 'Proxy (login:password@ip:port)']

    df = pd.DataFrame(data, columns=columns)
    df['Name'] = df['Name'].astype(str)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")
"""