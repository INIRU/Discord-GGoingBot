import discord
import json
import asyncio

from commands.etc import Util
from discord.ext import commands, tasks

with open("./database/bot_config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)


class GGoingClient(commands.Bot):
    __color__ = 0xb61f75

    def __init__(self):
        super().__init__(command_prefix=['g.'], case_insensitive=True, owner_ids=[247305812123320321, 340124004599988234, 484323677475831818, 332512584261435394],
                         description="꼬잉봇", chunk_guilds_at_startup=True, intents=discord.Intents.all())
        self.remove_command('help')

    def setup(self):
        Util.Bot.load_cogs(self)

    def run(self):
        self.setup()

        print("봇을 구동합니다.")
        super().run(data["token"], bot=True, reconnect=True)

    async def on_ready(self):
        print(f"Connected to Discord (latency: {self.latency*1000:,.0f} ms).")
        print(f"Name: {self.user.name} | ID: {self.user.id}")


if __name__ == "__main__":
    GGoingClient().run()
