import discord
import json
import typing
import asyncio
import datetime
import chat_exporter
import io

from discord.ext import commands


class ticket_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 785479453106241566:
            if not message.author.guild_permissions.administrator:
                await message.delete()

    @commands.command(name="ticket", alises=["티켓", "지원채널"])
    async def _ticket(self, message, *, desc: typing.Optional[str] = "없음"):
        await message.message.delete()
        if message.channel.category.id == 785472273091526676:
            return await message.send(f"{message.author.mention}, 지원 카테고리에서는 사용할 수 없습니다.")
        with open("./database/bot_config.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        category = self.bot.get_channel(785472273091526676)
        overwrites = {
            message.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, manage_channels=True, manage_roles=True, read_message_history=True),
            message.author: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
            message.guild.default_role: discord.PermissionOverwrite(
                read_messages=False)
        }
        channel = await message.guild.create_text_channel(name=f"지원_{data['ticket']:04d}", topic=f"{str(message.author)} ( {message.author.id} ) 님의 티켓입니다.", overwrites=overwrites, category=category, reason=f"{str(message.author)}님의 티켓 개설 요청입니다.")
        emb = discord.Embed(
            title=f"지원 - #{data['ticket']:04d}", color=self.bot.__color__)
        emb.description = f"""
**지원 내용:** {desc}\n
*잠시만 기다려주세요. 관리팀이 최대한 빨리 확인하고 답장할 거에요!*
"""
        emb.set_footer(text=f"지원 - {message.author}",
                       icon_url=message.author.avatar_url)
        msg = await channel.send(embed=emb)
        await msg.pin()
        data["ticket"] += 1
        with open('./database/bot_config.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @commands.command(name="close", aliases=["닫기"])
    async def _close(self, message):
        await message.message.delete()
        if message.channel.category.id != 785472273091526676:
            return await message.send(f"{message.author.mention}, 지원 채널에서만 사용할 수 있습니다.")
        if str(message.author.id) in message.channel.topic or message.author.guild_permissions.administrator:
            await message.send(f"{message.author.mention}, **`5`**초 후에 채널이 비활성화 됩니다.")
            await asyncio.sleep(5)
            ticket_id = message.channel.name[-4:]
            transcript = await chat_exporter.export(message.channel, set_timezone="Asia/Seoul")
            transcript_file = discord.File(io.BytesIO(
                transcript.encode()), filename=f"transcript-{message.channel.name}.html")
            await message.channel.delete(reason="지원 마침")
            log_channel = await self.bot.fetch_channel(802102463888883753)
            ids = message.channel.topic.replace(
                "(", "_").replace(")", "_").split("_")[1]
            user = message.guild.get_member(int(ids))
            emb = discord.Embed(
                color=0x00c934, timestamp=datetime.datetime.utcnow())
            emb.set_author(name=user, icon_url=user.avatar_url)
            emb.add_field(name="**생성자:**", value=user.mention)
            emb.add_field(name="**접수 번호:**", value=f"**{ticket_id}**")
            emb.add_field(name="**닫은 사람:**", value=message.author.mention)
            await log_channel.send(embed=emb, file=transcript_file)


def setup(bot):
    bot.add_cog(ticket_command(bot))
