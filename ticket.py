# pylint: disable=no-member

import discord
import json
import typing
import asyncio
import datetime

from discord.ext import commands, tasks
from dateutil.relativedelta import relativedelta


class ticket_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket = []
    # π©

    @commands.Cog.listener()
    async def on_ready(self):
        self.auto_channel_delete.start()

    @tasks.loop(seconds=10)
    async def auto_channel_delete(self):
        now = datetime.datetime.now()
        with open("./database/ticket.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        if str((now.month)) in data["ticket_channel"]:
            for channel_id in data["ticket_channel"][str(now.month)]:
                if self.bot.get_channel(channel_id) is not None:
                    await self.bot.get_channel(channel_id).delete(reason="2λ¬μ  μ§μμ΄ μ’λ£λμμ΅λλ€.")
            del data["ticket_channel"][str(now.month)]
            with open('./database/ticket.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

    async def create_channel(self, member, guild):
        with open("./database/ticket.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        self.ticket.append(member.id)
        category = self.bot.get_channel(785472273091526676)
        overwrites = {
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, manage_channels=True, manage_roles=True, read_message_history=True),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False)
        }
        chn = await guild.create_text_channel(name=f"πγ£λ¬Έμ_{data['ticket']:04d}", topic=f"{str(member)} ( {member.id} ) λμ ν°μΌμλλ€.", overwrites=overwrites, category=category, reason=f"{member}λμ ν°μΌ κ°μ€ μμ²­μλλ€.")
        emb = discord.Embed(
            title=f"λ¬Έμ - #{data['ticket']:04d}", color=0x019762)
        emb.description = (
            "**μ μλ§ κΈ°λ€λ €μ£ΌμΈμ. κ΄λ¦¬νμ΄ μ΅λν λΉ¨λ¦¬ νμΈνκ³  λ΅μ₯ν  κ±°μμ!**\n\n"

            "> `ν°μΌμ λ«μΌμλ €λ©΄ μλμ λ°μ(πΊ)μ λλ¬μ£ΌμΈμ. (κ΄λ¦¬μ λλ ν°μΌ μμ±μ)`"
        )
        msg = await chn.send(embed=emb, content=member.mention)
        await msg.add_reaction("πΊ")
        await msg.pin()
        data["ticket"] += 1
        with open('./database/ticket.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    async def delete_channel(self, guild, channel_id, member):
        channel = self.bot.get_channel(channel_id)
        user_id = (channel.topic.split("(")[1]).split(")")[0]
        user = guild.get_member(int(user_id))
        for i, x in enumerate(self.ticket):
            if x == user.id:
                del self.ticket[i]
        if user is not None:
            await channel.set_permissions(user, send_messages=False, read_messages=True, reason=f"{member}λμ ν°μΌ νκΈ° μμ²­.")
        await channel.edit(name=channel.name.replace("λ¬Έμ", "λ«ν"), category=self.bot.get_channel(785473331696107570))
        now = datetime.datetime.now()
        with open("./database/ticket.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        if str((now + relativedelta(months=2)).month) not in data["ticket_channel"]:
            data["ticket_channel"][str(
                (now + relativedelta(months=2)).month)] = []
        data["ticket_channel"][str(
            (now + relativedelta(months=2)).month)].append(channel_id)
        with open('./database/ticket.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        emb = discord.Embed(
            title=f"μ’λ£ - #{channel.name[-4:]}", color=0x019762)
        emb.description = (
            f"**`πγ£λ¬Έμ_{channel.name[-4:]}({channel.id})` μ§μμ΄ μ’λ£λμμ΅λλ€.**\n\n"

            "> `ν°μΌμ λ€μ νμ±ν μλμ λ°μ(β»)μ λλ¬μ£ΌμΈμ.`\n"
            "**`[!] νμ±νκ° μλλ€λ©΄ κΌ¬μλ΄ κ°μΈDMμλ€κ° λ©μΈμ§λ₯Ό νλ²λ§ μ μ‘νμ¬μ£ΌμΈμ.`**"
        )
        msg = await user.send(embed=emb)
        await msg.add_reaction("β»")

    async def re_create_channel(self, msg, user):
        self.ticket.append(user.id)
        embed_data = msg.embeds[0]
        chn_id = (embed_data.description.split("(")[1]).split(")")[0]
        with open("./database/ticket.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        for tc in list(data["ticket_channel"].keys()):
            if chn_id in data["ticket_channel"][tc]:
                for i, x in enumerate(data["ticket_channel"][tc]):
                    if x == chn_id:
                        del data["ticket_channel"][tc][i]
        channel = self.bot.get_channel(int(chn_id))
        if user is not None:
            await channel.set_permissions(user, read_messages=True, send_messages=True, attach_files=True, embed_links=True, reason=f"{user}λμ ν°μΌ νμ±ν μμ²­")
        await channel.edit(name=channel.name.replace("λ«ν", "λ¬Έμ"), category=self.bot.get_channel(785472273091526676))
        emb = discord.Embed(
            title=f"λ¬Έμ - #{channel.name[-4:]}", color=0x019762)
        emb.description = (
            "**μ μλ§ κΈ°λ€λ €μ£ΌμΈμ. κ΄λ¦¬νμ΄ μ΅λν λΉ¨λ¦¬ νμΈνκ³  λ΅μ₯ν  κ±°μμ!**\n\n"

            f"> [ν°μΌ λΉνμ±ν]({((await channel.pins())[0]).jump_url})\n"
            "`[!] ν°μΌμ λ«μΌλ €λ©΄ μκ°μ΄ νμν©λλ€.`"
        )
        msg = await channel.send(embed=emb, content=user.mention)

    @commands.command(name="λ¬Έμ")
    @commands.has_permissions(administrator=True)
    async def _ticket(self, message):
        emb = discord.Embed(title="κ³ κ°μΌν°μ λ¬ΈμνκΈ°", color=0x019762)
        emb.description = (
            "**μ΄ λ°μ(π©)μ λλ₯΄λ©΄ λ¬Έμ μ±λμ΄ μμ±λ©λλ€.**\n\n"
            "> πΊ**μ£Όμμ¬ν­**\n"
            "`- μ§μμ±λμ μμ±ν λ¨Όμ  μ©κ±΄μ λ§ν΄μ£ΌμΈμ.`\n"
            "`- νμλ‘ μ§μ ν°μΌμ μμ±νμ§ λ§μμ£ΌμΈμ.`\n"
            "`- μλ΄μ λλ μ€ννλ₯Ό μ‘΄μ€νμ¬ μ£ΌμΈμ. (μΉΌλ΅νλ κΈ°κ³κ° μλλλ€.)`"
        )
        msg = await message.send(embed=emb)
        await msg.add_reaction("π©")

    @commands.Cog.listener("on_raw_reaction_add")
    async def create_ticket(self, payload):
        if payload.guild_id is None:
            return
        channels = payload.channel_id
        guild_id = payload.guild_id
        guild = discord.utils.find(
            lambda g: g.id == guild_id, self.bot.guilds)
        member = discord.utils.find(
            lambda m: m.id == payload.user_id, guild.members)
        if channels == 785479453106241566 and str(payload.emoji) == "π©" and not member.bot:
            msg = await self.bot.get_channel(channels).fetch_message(payload.message_id)
            await msg.remove_reaction("π©", member)
            if member.id not in self.ticket:
                await self.create_channel(member, guild)
            elif member.id in self.ticket:
                await member.send(f"{member.mention}, μ΄λ―Έ μμ±λ ν°μΌμ΄ μμ΅λλ€.")

    @commands.Cog.listener("on_raw_reaction_add")
    async def delete_ticket(self, payload):
        if payload.guild_id is None:
            return
        channels = payload.channel_id
        guild_id = payload.guild_id
        guild = discord.utils.find(
            lambda g: g.id == guild_id, self.bot.guilds)
        member = discord.utils.find(
            lambda m: m.id == payload.user_id, guild.members)
        if self.bot.get_channel(channels).category_id == 785472273091526676 and str(payload.emoji) == "πΊ" and not member.bot:
            msg = await self.bot.get_channel(channels).fetch_message(payload.message_id)
            await msg.remove_reaction("πΊ", member)
            await self.delete_channel(guild, channels, member)

    @commands.Cog.listener("on_raw_reaction_add")
    async def re_create_ticket(self, payload):
        if payload.guild_id is not None:
            return
        channel = discord.utils.get(
            self.bot.private_channels, id=payload.channel_id)
        if str(channel.type) == "private":
            user = discord.utils.find(
                lambda m: m.id == payload.user_id, self.bot.users)
            if str(payload.emoji) == "β»" and not user.bot:
                msg = await channel.fetch_message(payload.message_id)
                await self.re_create_channel(msg, user)
                await msg.delete()


def setup(bot):
    bot.add_cog(ticket_command(bot))
