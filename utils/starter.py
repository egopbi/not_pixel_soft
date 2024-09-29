import random 
import datetime
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
from utils.notpixel import NotPx, get_web_app_data


async def autopainter(thread: int, session_name: str, NotPxClient: NotPx, client: TelegramClient):
    logger.info(f"Thread {thread} | {session_name} | **Painter:** Auto painting started!")
    # print(f'@@@@@@@@@@@@@@@@@@@@@@@@@@@\n{NotPxClient}\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    while True:
        await NotPxClient.update_headers(client=client)
        async with aiohttp.TCPConnector(verify_ssl=False) as connector:
            async with aiohttp.ClientSession(
                headers=NotPxClient.session_headers,
                trust_env=True,
                connector=connector,
                timeout=aiohttp.ClientTimeout(300)
                ) as aiohttp_session:
                print(f'%%%%%%%%%%%%%%%%%%%%%%%%%\n\n{session_name} | Autopainter aiohttp_session is: {aiohttp_session}\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%') # Разные в разных сессиях
    
                try:
                    await asyncio.sleep(random.randint(2, 4))
                    acc_data = await NotPxClient.accountStatus(aiohttp_session)
                    logger.info(f"Thread {thread} | {session_name} | **Painter:** account_data is {acc_data} ")
                    if not acc_data:
                        await asyncio.sleep(5)
                        continue
                    else:
                        charges = acc_data['charges']

                    try:
                        if charges > 0:    
                            for _ in range(charges):
                                balance = await NotPxClient.autoPaintPixel(aiohttp_session) #ошибка в этой функции
                                logger.success(f"Thread {thread} | {session_name} | **Painter:** 1 Pixel painted successfully! User new balance: {balance}")

                                t = random.randint(1,6)
                                logger.info(f"Thread {thread} | {session_name} | **Painter antidetect:** Sleeping for {t} seconds...")
                                await asyncio.sleep(t)
                    except:
                        logger.error(f"Thread {thread} | {session_name} | **Painter:** RequestError. Sleeping for 20s...")
                        await asyncio.sleep(20)
                                

                except aiohttp.ClientConnectionError:
                    logger.error(f"Thread {thread} | {session_name} | **Painter:** ConnectionError. Sleeping for 5s...")
                    await asyncio.sleep(5)

                except urllib3.exceptions.NewConnectionError:
                    logger.error(f"Thread {thread} | {session_name} | **Painter:** NewConnectionError. Sleeping for 5s...")
                    await asyncio.sleep(5)
        
        d = random.randint(1800, 6000) 
        logger.info(f"Thread {thread} | {session_name} | **Painter:** No charge avaliable. Sleeping for {d} seconds...")
        await asyncio.sleep(d)


async def mine_claimer(thread: int, session_name: str, NotPxClient: NotPx, client: TelegramClient):
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
                    acc_data = await NotPxClient.accountStatus(aiohttp_session) #ошибка в этой функции
                
                    print(f'%%%%%%%%%%%%%%%%%%%%%%%%%\n\n{session_name} | Mineclaimer aiohttp_session is: {aiohttp_session}\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%') # Разные в разных сессиях
                    if not acc_data:
                        logger.error(f"Thread {thread} | {session_name} | **Miner:** No acc_data! ")
                        await asyncio.sleep(5)
                        continue
                    else:
                        logger.info(f"Thread {thread} | {session_name} | **Miner:** account_data is {acc_data} ")
                        
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


        sleep_time = random.randint(3600,15000)
        logger.info(f"Thread {thread} | {session_name} | **Miner:** Sleeping for {sleep_time} seconds...")
        await asyncio.sleep(sleep_time)


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None], web_app_query: str, client: TelegramClient):
    NotPxClient = NotPx(
        thread=thread,
        session_name=pathlib.Path(config.SESSIONS_PATH, session_name),
        phone_number=phone_number,
        proxy=proxy,
        web_app_query=web_app_query,
        )
    # print(f'\n\n********************\n{thread}\n{session_name}\n{phone_number}\n{proxy}\n{NotPxClient.web_app_query}\n**********************')
    session_name = session_name + '.session'
    await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
    await asyncio.gather(
    autopainter(thread=thread, session_name=session_name, NotPxClient=NotPxClient, client=client),
    mine_claimer(thread=thread, session_name=session_name, NotPxClient=NotPxClient, client=client)
    )


           
# ФУнкция не готова, не трогал изменения с webappquery
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