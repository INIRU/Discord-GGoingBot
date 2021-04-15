# pylint: disable=no-member

import os
import json

from discord.ext.commands import bot


class Bot:
    def __init__(self, bot):
        self.bot = bot

    def load_cogs(self):
        with open("./database/bot_config.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        failed_list = []
        print("꼬잉봇의 명령어를 불러오겠습니다.")
        for folder in data["folder"]:
            for cogs in os.listdir(f"commands/{folder}"):
                if cogs.endswith(".py"):
                    try:
                        self.load_extension(f"commands.{folder}.{cogs[:-3]}")
                        print(f"성공 {folder}/{cogs}")
                    except Exception as e:
                        print(f"실패 {e.__class__.__name__}: {e}")
                        failed_list.append(
                            f"{cogs}: {e.__class__.__name__}: {e}\n")
        if failed_list:
            print(f"\n볼러오기를 실패한 파일 \n{''.join(failed_list)}")
        print("완료!")
        return failed_list
