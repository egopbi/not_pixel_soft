import random 
import datetime
import asyncio
import urllib3
import pandas as pd
import aiohttp

import config
from utils.core.telegram import Accounts
from utils.core import logger
from utils.notpixel import NotPx

async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    NotPxClient = NotPx(thread=thread, session_name=session_name, phone_number=phone_number, proxy=proxy)

    await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
    logger.info(f"Thread {thread} | {NotPxClient.account} | Auto painting started!")

    while True:
        try:
            charges = await NotPxClient.accountStatus()
            if not charges:
                asyncio.sleep(5)
                continue
            else:
                charges = charges['charges']

            if charges > 0:
                for _ in range(charges):
                    balance = await NotPxClient.autoPaintPixel()
                    logger.success(f"Thread {thread} | {NotPxClient.account} | 1 Pixel painted successfully! User new balance: {balance}")

                    t = random.randint(1,6)
                    logger.info(f"Thread {thread} | {NotPxClient.account} | Painter antidetect: Sleeping for {t} ...")
                    asyncio.sleep(t)
            else:
                logger.info(f"Thread {thread} | {NotPxClient.account} | Painter: No charge avaliable. Sleeping for 10 minutes...")
                asyncio.sleep(600)

        except aiohttp.ClientConnectionError:
            logger.error(f"Thread {thread} | {NotPxClient.account} | Painter: ConnectionError. Sleeping for 5s...")
            asyncio.sleep(5)

        except urllib3.exceptions.NewConnectionError:
            logger.error(f"Thread {thread} | {NotPxClient.account} | Painter: NewConnectionError. Sleeping for 5s...")
            asyncio.sleep(5)
           

async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(NotPx(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Phone number', 'Name', 'Points', 'Session', 'Thread', 'Proxy (login:password@ip:port)']

    df = pd.DataFrame(data, columns=columns)
    df['Name'] = df['Name'].astype(str)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")
