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
    # 📩

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
                    await self.bot.get_channel(channel_id).delete(reason="2달전 지원이 종료되었습니다.")
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
        chn = await guild.create_text_channel(name=f"💌ㅣ문의_{data['ticket']:04d}", topic=f"{str(member)} ( {member.id} ) 님의 티켓입니다.", overwrites=overwrites, category=category, reason=f"{member}님의 티켓 개설 요청입니다.")
        emb = discord.Embed(
            title=f"문의 - #{data['ticket']:04d}", color=0x019762)
        emb.description = (
            "**잠시만 기다려주세요. 관리팀이 최대한 빨리 확인하고 답장할 거에요!**\n\n"

            "> `티켓을 닫으시려면 아래의 반응(🔺)을 눌러주세요. (관리자 또는 티켓 생성자)`"
        )
        msg = await chn.send(embed=emb, content=member.mention)
        await msg.add_reaction("🔺")
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
            await channel.set_permissions(user, send_messages=False, read_messages=True, reason=f"{member}님의 티켓 파기 요청.")
        await channel.edit(name=channel.name.replace("문의", "닫힘"), category=self.bot.get_channel(785473331696107570))
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
            title=f"종료 - #{channel.name[-4:]}", color=0x019762)
        emb.description = (
            f"**`💌ㅣ문의_{channel.name[-4:]}({channel.id})` 지원이 종료되었습니다.**\n\n"

            "> `티켓을 다시 활성화 아래의 반응(♻)을 눌러주세요.`\n"
            "**`[!] 활성화가 안된다면 꼬잉봇 개인DM에다가 메세지를 한번만 전송하여주세요.`**"
        )
        msg = await user.send(embed=emb)
        await msg.add_reaction("♻")

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
            await channel.set_permissions(user, read_messages=True, send_messages=True, attach_files=True, embed_links=True, reason=f"{user}님의 티켓 활성화 요청")
        await channel.edit(name=channel.name.replace("닫힘", "문의"), category=self.bot.get_channel(785472273091526676))
        emb = discord.Embed(
            title=f"문의 - #{channel.name[-4:]}", color=0x019762)
        emb.description = (
            "**잠시만 기다려주세요. 관리팀이 최대한 빨리 확인하고 답장할 거에요!**\n\n"

            f"> [티켓 비활성화]({((await channel.pins())[0]).jump_url})\n"
            "`[!] 티켓을 닫으려면 시간이 필요합니다.`"
        )
        msg = await channel.send(embed=emb, content=user.mention)

    @commands.command(name="문의")
    @commands.has_permissions(administrator=True)
    async def _ticket(self, message):
        emb = discord.Embed(title="고객센터에 문의하기", color=0x019762)
        emb.description = (
            "**이 반응(📩)을 누르면 문의 채널이 생성됩니다.**\n\n"
            "> 🔺**주의사항**\n"
            "`- 지원채널을 생성후 먼저 용건을 말해주세요.`\n"
            "`- 허위로 지원 티켓을 생성하지 말아주세요.`\n"
            "`- 상담원 또는 스태프를 존중하여 주세요. (칼답하는 기계가 아닙니다.)`"
        )
        msg = await message.send(embed=emb)
        await msg.add_reaction("📩")

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
        if channels == 785479453106241566 and str(payload.emoji) == "📩" and not member.bot:
            msg = await self.bot.get_channel(channels).fetch_message(payload.message_id)
            await msg.remove_reaction("📩", member)
            if member.id not in self.ticket:
                await self.create_channel(member, guild)
            elif member.id in self.ticket:
                await member.send(f"{member.mention}, 이미 생성된 티켓이 있습니다.")

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
        if self.bot.get_channel(channels).category_id == 785472273091526676 and str(payload.emoji) == "🔺" and not member.bot:
            msg = await self.bot.get_channel(channels).fetch_message(payload.message_id)
            await msg.remove_reaction("🔺", member)
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
            if str(payload.emoji) == "♻" and not user.bot:
                msg = await channel.fetch_message(payload.message_id)
                await self.re_create_channel(msg, user)
                await msg.delete()


def setup(bot):
    bot.add_cog(ticket_command(bot))
