import discord

from discord.ext import commands


class emoji_event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channels = payload.channel_id
        guild_id = payload.guild_id
        guild = discord.utils.find(
            lambda g: g.id == guild_id, self.bot.guilds)
        member = discord.utils.find(
            lambda m: m.id == payload.user_id, guild.members)
        if channels == 620258074002849832:
            if str(payload.emoji) == "✅":
                role = discord.utils.get(guild.roles, id=757557473988313108)
                await member.add_roles(role)


def setup(bot):
    bot.add_cog(emoji_event(bot))
