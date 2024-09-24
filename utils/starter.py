import random 
import datetime
import asyncio
import urllib3
import pandas as pd
import aiohttp

import pathlib

import config

from utils.core.telegram import Accounts
from utils.core import logger
from utils.notpixel import NotPx, get_web_app_data


async def autopainter(thread: int, session_name: str, NotPxClient: NotPx):
    logger.info(f"Thread {thread} | {session_name} | **Painter:** Auto painting started!")
    print(f'@@@@@@@@@@@@@@@@@@@@@@@@@@@\n{NotPxClient}\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    while True:
        try:
            charges = await NotPxClient.accountStatus() #ошибка в этой функции
            print(f'!!!!!!!!!!!!!!!!!!!\n\n{charges}\n\n!!!!!!!!!!!!!!!!!!!!!!')
            if not charges:
                await asyncio.sleep(5)
                continue
            else:
                charges = charges['charges']

            if charges > 0:
                for _ in range(charges):
                    balance = await NotPxClient.autoPaintPixel() #ошибка в этой функции
                    logger.success(f"Thread {thread} | {session_name} | **Painter:** 1 Pixel painted successfully! User new balance: {balance}")

                    t = random.randint(1,6)
                    logger.info(f"Thread {thread} | {session_name} | **Painter antidetect:** Sleeping for {t} seconds...")
                    await asyncio.sleep(t)
            else:
                d = random.randint(900, 2400)
                logger.info(f"Thread {thread} | {session_name} | **Painter:** No charge avaliable. Sleeping for {d} seconds...")
                await asyncio.sleep(d)

        except aiohttp.ClientConnectionError:
            logger.error(f"Thread {thread} | {session_name} | **Painter:** ConnectionError. Sleeping for 5s...")
            await asyncio.sleep(5)

        except urllib3.exceptions.NewConnectionError:
            logger.error(f"Thread {thread} | {session_name} | **Painter:** NewConnectionError. Sleeping for 5s...")
            await asyncio.sleep(5)

async def mine_claimer(thread: int, session_name: str, NotPxClient: NotPx):
    logger.info(f"Thread {thread} | {session_name} | **Miner:** Mine claiming started!") 
    
    while True:
        acc_data = await NotPxClient.accountStatus()
        from_start = acc_data['fromStart']
        speed_per_second = acc_data['speedPerSecond']
        
        if from_start * speed_per_second > 2:
            claimed_count = await NotPxClient.claim_mining()
            if claimed_count is None:
                logger.info(f"Thread {thread} | {session_name} | **Miner:** Error request. Sleeping for 1 hour...")
                await asyncio.sleep(3600)
            else:
                claimed_count = round(claimed_count,2)
                logger.success(f"Thread {thread} | {session_name} | **Miner:** {claimed_count} NotPx token was claimed.")
        sleep_time = random.randint(3600,15000)
        logger.info(f"Thread {thread} | {session_name} | **Miner:** Sleeping for {sleep_time} seconds...")
        await asyncio.sleep(sleep_time)


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None], web_app_query: str):
    # NotPxClient разные
    NotPxClient = NotPx(
        thread=thread,
        session_name=pathlib.Path(config.SESSIONS_PATH, session_name),
        phone_number=phone_number,
        proxy=proxy,
        web_app_query=web_app_query,
        )
    print(f'\n\n********************\n{thread}\n{session_name}\n{phone_number}\n{proxy}\n{NotPxClient.web_app_query}\n**********************')
    # Даже при удалении основной сессии все равно идут на нее запросы
    session_name = session_name + '.session'
    await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
    print('\n////////////////////////////\n', session_name, '\n/////////////////////////////\n')
    await asyncio.gather(
    autopainter(thread=thread, session_name=session_name, NotPxClient=NotPxClient),
    mine_claimer(thread=thread, session_name=session_name, NotPxClient=NotPxClient)
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