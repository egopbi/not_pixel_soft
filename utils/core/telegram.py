import asyncio
import os
import pathlib

from telethon.sync import TelegramClient
from dotenv import load_dotenv

import config
from utils.core import logger, load_from_json, save_list_to_file, save_to_json, get_all_lines

load_dotenv()


def parse_proxy(proxy):
        return {
            "proxy_type": config.PROXY['TYPE']['TG'],
            "addr": proxy.split(":")[1].split("@")[1],
            "port": int(proxy.split(":")[2]),
            "username": proxy.split(":")[0],
            "password": proxy.split(":")[1].split("@")[0]
        } if proxy else None


class Accounts:
    def __init__(self):
        self.workdir = config.WORKDIR
        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")

    @staticmethod
    def get_available_accounts(sessions: list):
        available_accounts = []

        if config.PROXY['USE_PROXY_FROM_DOTENV']:
            for session in sessions:
                proxy_name = "PROXY_" + str(session)
                proxy = None
                try:
                    proxy = os.getenv(proxy_name)
                except:
                    logger.error(f"Proxy with name {proxy_name} doesn't exist")
                available_accounts.append({
                    'session_name': session,
                    'phone_number': '+0',
                    'proxy': proxy
                })

        else:
            accounts_from_json = load_from_json('sessions/accounts.json')

            if not accounts_from_json:
                raise ValueError("Have not account's in sessions/accounts.json")

            for session in sessions:
                for saved_account in accounts_from_json:
                    if saved_account['session_name'] == session:
                        available_accounts.append(saved_account)
                        break

        return available_accounts

    def parse_sessions(self):
        sessions = [file.replace(".session", "") for file in os.listdir(self.workdir) if file.endswith(".session")]
        logger.info(f"Searched sessions: {len(sessions)}.")
        return sessions

    async def check_valid_account(self, account: dict):
        session_name, phone_number, proxy = account.values()

        try:
            
            proxy_dict = parse_proxy(proxy) if proxy else None

            client = TelegramClient(
                session=pathlib.Path(config.SESSIONS_PATH, session_name), 
                api_id=self.api_id, 
                api_hash=self.api_hash,
                proxy=proxy_dict
                )
            
            await asyncio.wait_for(client.connect(), timeout=config.TIMEOUT)
            connect = client.is_connected()
            if connect:
                await client.get_me()
                await client.disconnect()
                return account
            else:
                await client.disconnect()
        except:
            raise ValueError("Account isn't valid")

    async def check_valid_accounts(self, accounts: list):
        logger.info("Checking accounts for valid...")

        tasks = []
        for account in accounts:
            tasks.append(asyncio.create_task(self.check_valid_account(account)))

        v_accounts = await asyncio.gather(*tasks)

        valid_accounts = [account for account, is_valid in zip(accounts, v_accounts) if is_valid]
        invalid_accounts = [account for account, is_valid in zip(accounts, v_accounts) if not is_valid]
        logger.success(f"Valid accounts: {len(valid_accounts)}; Invalid: {len(invalid_accounts)}")

        return valid_accounts, invalid_accounts

    async def get_accounts(self):
        sessions = self.parse_sessions()
        print(f"\n\n\n----------------{sessions}---------------\n\n\n")
        available_accounts = self.get_available_accounts(sessions)

        if not available_accounts:
            raise ValueError("Have not available accounts!")
        else:
            logger.success(f"Search available accounts: {len(available_accounts)}.")

        valid_accounts, invalid_accounts = await self.check_valid_accounts(available_accounts)

        if invalid_accounts:
            save_list_to_file(f"{ config.WORKDIR}invalid_accounts.txt", invalid_accounts)
            logger.info(f"Saved {len(invalid_accounts)} invalid account(s) in { config.WORKDIR}invalid_accounts.txt")

        if not valid_accounts:
            raise ValueError("Have not valid sessions")
        else:
            return valid_accounts

    async def create_sessions(self):
        while True:
            session_name = input('\nInput the name of the session (press Enter to exit): ')
            if not session_name: return

            if config.PROXY['USE_PROXY_FROM_DOTENV']:
                proxy_name = "PROXY_" + str(session_name)
                try:
                    proxy = os.getenv(proxy_name)
                except:
                    logger.error(f"Proxy with name {proxy_name} doesn't exist")
                    proxy = input("Input the proxy in the format login:password@ip:port (press Enter to use without proxy): ")

            dict_proxy = parse_proxy(proxy)

            client = TelegramClient(
                session=pathlib.Path(config.SESSIONS_PATH, session_name),
                api_id=self.api_id,
                api_hash=self.api_hash,
                proxy=dict_proxy,
            )

            async with client:
                me = await client.get_me()
            
            phone_number = '+' + me.phone

            save_to_json(f'{ config.WORKDIR}accounts.json', dict_={
                "session_name": session_name,
                "phone_number": phone_number,
                "proxy": ""
            })
            logger.success(f'Added an account {me.username} ({me.first_name}) | +{me.phone}')