import os
import asyncio
import pathlib
from itertools import zip_longest

from utils.core.telegram import Accounts
from utils.starter import start # , stats
from utils.core import get_all_lines
from utils.notpixel import get_web_app_data
import config


async def main():
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
    
        # Почему-то все запросы идут на один акк
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            print(f'\n(((((((({thread})))))))))\n==================\n{account}\n=======================')
            async  with asyncio.Lock() as lock:
                tg_sessions[session_name] = get_web_app_data(lock) 
            tasks.append(asyncio.create_task(start(
                session_name=session_name, 
                phone_number=phone_number, 
                thread=thread, 
                proxy=proxy,
                web_app_query=tg_sessions[session_name],
                )))
        print(tg_sessions)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
