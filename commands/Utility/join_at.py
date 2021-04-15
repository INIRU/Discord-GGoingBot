import discord

from discord.ext import commands


class join_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="서버가입일", aliases=["joindate"])
    @commands.guild_only()
    async def _joindate(self, message):
        now = message.author.joined_at
        await message.send(f"{message.author.mention}, 당신의 {message.guild.name}가입일은 {now.strftime('`%Y. %m. %d` **`%p %I:%M`**').replace('PM', '오후').replace('AM', '오전')}")


def setup(bot):
    bot.add_cog(join_command(bot))
