import os
import asyncio
import pathlib
from itertools import zip_longest

from telethon.sync import TelegramClient

from utils.core.telegram import Accounts
from utils.starter import start # , stats
from utils.core import get_all_lines
from utils.notpixel import get_web_app_data
import config

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

async def main():
    # lock = asyncio.Lock() 
    print("Soft's author: EGORKA Ebana v rot")
    action = int(input("Select action:\n1. Start soft\n2. Get statistics\n3. Create sessions\n\n> "))

    if not os.path.exists('sessions'): os.mkdir('sessions')

    if config.PROXY['USE_PROXY_FROM_FILE']:
        if not os.path.exists(config.PROXY['PROXY_PATH']):
            with open(config.PROXY['PROXY_PATH'], 'w') as f:
                f.write("")
    else:
        if not os.path.exists('sessions/accounts.json'):
            with open("sessions/accounts.json", 'w') as f:
                f.write("[]")

    if action == 3:
        await Accounts().create_sessions()

    # if action == 2:
    #     await stats()

    if action == 1:
        accounts = await Accounts().get_accounts()

        tasks = []
        tg_sessions = {}
    
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            print(f'\n(((((((({thread})))))))))\n==================\n{account}\n=======================')
            client = await TelegramClient("NotPx_Auto",api_id,api_hash).start()
            # async with lock:
            #     tg_sessions[session_name] = await get_web_app_data(lock) 
            tg_sessions[session_name] = await get_web_app_data(client)
            tasks.append(asyncio.create_task(start(
                session_name=session_name, 
                phone_number=phone_number, 
                thread=thread, 
                proxy=proxy,
                web_app_query=tg_sessions[session_name],
                )))
        # print(f'\n^^^^^^^^^^^^^^^^^^^^^^^^^^^\n{tg_sessions}\n^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
