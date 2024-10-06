import os
import asyncio

from telethon.sync import TelegramClient

from utils.core.telegram import Accounts
from utils.starter import start # , stats
from utils.core import logger, load_from_json
from utils.core.telegram import parse_proxy
from utils.notpixel import get_web_app_data
import config

# api_id = os.getenv("API_ID_morenocesar")
# api_hash = os.getenv("API_HASH_morenocesar")

async def main():
    print("Soft's author: Eeee Gorka Ebana v rot")
    action = int(input("Select action:\n1. Start soft\n2. Get statistics\n3. Create sessions\n\n> "))

    if not os.path.exists('sessions'): os.mkdir('sessions')

    if action == 3:
        await Accounts().create_sessions()

    # if action == 2:
    #     await stats()

    if action == 1:
        # Downloads API's for every account
        try:
            accounts_from_json = load_from_json('sessions/accounts.json')
            api_dict = {}

            for account in accounts_from_json:
                session_name = account['session_name']
                api_id_name = "API_ID_" + str(session_name)
                api_hash_name = "API_HASH_" + str(session_name)
                api_id = os.getenv(api_id_name)
                api_hash = os.getenv(api_hash_name)
                api_dict[session_name] = (api_id, api_hash)
        except:
            logger.error("YOU HAVE NO SESSION ACCOUNTS YET")
        
        logger.info(f"Your api dict is\n{api_dict}")
        
        accounts = await Accounts().get_accounts()

        tasks = []
        tg_sessions = {}
    
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            proxy = parse_proxy(proxy)
            print(f'\n(((((((({thread})))))))))\n==================\n{account}\n=======================')

            # print(f'\n\n\n========== BEFORE TELEGRAMCLIENT.START {session_name} ==========\n\n\n')
            client = await TelegramClient(f"NotPx_Auto_{session_name}",api_dict[session_name][0], api_dict[session_name][1], proxy=proxy).start()

            tg_sessions[session_name] = await get_web_app_data(client)
            tasks.append(asyncio.create_task(start(
                session_name=session_name, 
                phone_number=phone_number, 
                thread=thread, 
                proxy=proxy,
                web_app_query=tg_sessions[session_name],
                client=client
                )))
        # print(f'\n^^^^^^^^^^^^^^^^^^^^^^^^^^^\n{tg_sessions}\n^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
