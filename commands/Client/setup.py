import discord
import asyncio

from discord.ext import commands, tasks


class setup_client(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, message, error):
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            print(error)


def setup(bot):
    bot.add_cog(setup_client(bot))
