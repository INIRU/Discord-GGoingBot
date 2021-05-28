# pylint: disable=no-member

import discord
import aiohttp
import json
import datetime
import random
import typing
import asyncio
import sqlite3

from discord.ext import commands, tasks

top_dic = {}


class attendance_check(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('./database/User_Data/rank_data.json', 'r') as f:
            data = json.load(f)
        self.top_dic = data
        self.daily_rank_msg = []

    def rank_check(self, u_id):
        rank = 1
        type_x = False
        for i in range(len(list(self.top_dic.keys()))):
            if type_x == True:
                break
            for x in self.top_dic[str(i+1)]:
                if u_id in x:
                    type_x = True
                    rank = i + 1
                    break
        return rank

    def check_i(self, user, message):
        data = self.load_data(user.id)
        lastday = (datetime.datetime.strptime(
            str(data[3]), '%Y%m%d')).strftime("%Y년 %m월 %d일")
        with open('./database/User_Data/attendance_check.json', 'r') as f:
            ad_data = json.load(f)
        for role in ad_data["reward"]:
            r_rs = int((list(role.keys()))[0])
            if r_rs > (data[2]):
                role_name = str(discord.utils.get(
                    message.guild.roles, id=role[str(r_rs)]))
                break
        emb = discord.Embed(title=f"{user}님의 출석체크 정보",
                            timestamp=datetime.datetime.utcnow())
        emb.description = (
            "```cs\n"
            f"[시즌{ad_data['season']['season_name']} 순위] - {int(self.rank_check(user.id))}위\n"
            f"[전체 출석체크 횟수] - {data[2]}회\n"
            f"[시즌 출석체크 횟수] - {data[1]}회\n"
            f"[마지막 출첵일] - {lastday}\n"
            "\n```\n"
            f"> 다음 등급 {role_name} 까지 `{r_rs - data[2]}`회 남았습니다."
        )
        return emb

    @commands.Cog.listener()
    async def on_ready(self):
        self.attendance_check_top.start()
        self.attendance_check_sesaon.start()
        self.daily_rank_mistake.start()

    async def daily_rank(self, msg):
        with open('./database/User_Data/attendance_check.json', 'r') as f:
            data = json.load(f)
        guild = self.bot.get_guild(446763327499141120)
        rtop = discord.utils.get(guild.roles, id=825296383971688459)
        conn = sqlite3.connect(
            "database/User_Data/check.db", isolation_level=None)
        c = conn.cursor()
        day_messages = []
        channel = self.bot.get_channel(785850711316496426)
        nowday = int((datetime.datetime.now()).strftime("%Y%m%d"))
        async for message in channel.history(limit=len(guild.members)):
            if int((message.created_at + datetime.timedelta(hours=9)).strftime("%Y%m%d")) == nowday and len(message.embeds) > 0:
                day_messages.append(message)
        for i, x in enumerate(day_messages):
            if x.id == msg.id:
                break
        msg_emb_data = msg.embeds[0]
        msg_content_data = msg.mentions[0]
        emb = discord.Embed(color=msg_emb_data.color)
        emb.set_author(name=msg_emb_data.author.name,
                       icon_url=msg_emb_data.author.icon_url)
        for f in msg_emb_data.fields:
            value = f.value
            if f.name == "🏆 **내 순위:**":
                value = f"**`{len(guild.members)}`명 중 `{len(day_messages) - i}`위**"
            emb.add_field(name=f.name, value=value, inline=f.inline)
        emb.set_footer(text=msg_emb_data.footer.text)
        await msg.edit(embed=emb)
        if data["day"] != nowday:
            if (len(day_messages) - i) == 1:
                u_data = self.load_data(msg_content_data.id)
                await guild.get_member(data["top"]).remove_roles(rtop)
                await guild.get_member(msg_content_data.id).add_roles(rtop)
                data["top"] = msg_content_data.id
                data["day"] = nowday
                with open('./database/User_Data/attendance_check.json', 'w') as f:
                    json.dump(data, f, indent=4)
                c.execute("UPDATE attendancecheck SET top1 = ? WHERE id = ?",
                          (u_data[4]+1, msg_content_data.id))

    @tasks.loop(seconds=30)
    async def daily_rank_mistake(self):
        day_messages = []
        guild = self.bot.get_guild(446763327499141120)
        channel = self.bot.get_channel(785850711316496426)
        nowday = int((datetime.datetime.now()).strftime("%Y%m%d"))
        async for message in channel.history(limit=len(guild.members)):
            if int((message.created_at + datetime.timedelta(hours=9)).strftime("%Y%m%d")) == nowday and len(message.embeds) > 0:
                day_messages.append(message)
        for i, x in enumerate(reversed(day_messages)):
            y = int((x.embeds[0].fields[0].value[-7:]).replace("*",
                                                               "").replace("`", "").replace("위", "").replace(" ", ""))
            if (i + 1) != y:
                msg_emb_data = x.embeds[0]
                emb = discord.Embed(color=msg_emb_data.color)
                emb.set_author(name=msg_emb_data.author.name,
                               icon_url=msg_emb_data.author.icon_url)
                for f in msg_emb_data.fields:
                    value = f.value
                    if f.name == "🏆 **내 순위:**":
                        value = f"**`{len(guild.members)}`명 중 `{i + 1}`위**"
                    emb.add_field(name=f.name, value=value, inline=f.inline)
                emb.set_footer(text=msg_emb_data.footer.text)
                await x.edit(embed=emb)

    @tasks.loop(seconds=1)
    async def attendance_check_sesaon(self):
        with open('./database/User_Data/attendance_check.json', 'r') as f:
            data = json.load(f)
        nowday = int((datetime.datetime.now()).strftime("%Y%m"))
        if data["season"]["startday"] < nowday:
            conn = sqlite3.connect(
                "database/User_Data/check.db", isolation_level=None)
            c = conn.cursor()
            c.execute("SELECT * FROM attendancecheck")
            v = c.fetchall()
            top_u = []
            for t in self.top_dic["1"]:
                top_u.append(self.bot.get_user(t[0]).mention)
            for u in v:
                c.execute(
                    "UPDATE attendancecheck SET season_check = ? WHERE id = ?", (0, u[0]))
            await self.bot.get_channel(640032706058649642).send(
                "> **시즌이 변경되었습니다.**\n"
                f"**{data['season']['season_name']} 시즌**에서 **{data['season']['season_name']+1} 시즌**으로 변경되었습니다.\n**자 이제 모두 불타오르세요!**\n\n"
                "> 시즌이 변경되어 모든 시즌 출첵 횟수가 초기화 되었습니다.\n\n"
                f"**{data['season']['season_name']} 시즌** 1위: " +
                ", ".join(top_u)
            )
            data["season"]["season_name"] += 1
            data["season"]["startday"] = nowday
            with open('./database/User_Data/attendance_check.json', 'w') as f:
                json.dump(data, f, indent=4)

    @tasks.loop(seconds=60)
    async def attendance_check_top(self):
        top_dic = {}
        with open('./database/User_Data/attendance_check.json', 'r') as f:
            data = json.load(f)
        conn = sqlite3.connect(
            "database/User_Data/check.db", isolation_level=None)
        c = conn.cursor()
        c.execute("SELECT * FROM attendancecheck")
        v = c.fetchall()
        v.sort(key=lambda x: -x[1])
        msg = await self.bot.get_channel(826025817569099786).fetch_message(832202434176483328)
        emb = discord.Embed(
            title=f"**{data['season']['season_name']} 시즌**", timestamp=datetime.datetime.utcnow())
        v_check = v[1][1]
        i = 1
        for u in v:
            if v_check > u[1]:
                i += 1
                v_check = u[1]
            if v_check >= u[1]:
                if str(i) not in top_dic:
                    top_dic[str(i)] = []
                top_dic[str(i)].append(u)
        self.top_dic = top_dic
        with open('./database/User_Data/rank_data.json', 'w') as f:
            json.dump(self.top_dic, f, indent=4)
        await self.bot.get_channel(832821592559976458).send("출석체크 순위가 갱신되었습니다.", file=discord.File("./database/User_Data/rank_data.json"))
        for x in range(i):
            if (x + 1) == 11:
                break
            if (x + 1) == 1:
                text = "🥇"
            elif (x + 1) == 2:
                text = "🥈"
            elif (x + 1) == 3:
                text = "🥉"
            else:
                text = f"{x+1}위"
            if len(top_dic[str(x+1)]) > 1:
                if (x + 1) == 1:
                    top1_message = f"**{self.bot.get_user(top_dic[str(x+1)][0][0])} 외 {len(top_dic[str(x+1)])-1} 명 분들**"
                emb.add_field(
                    name=f"{text} {self.bot.get_user(top_dic[str(x+1)][0][0])} 외 {len(top_dic[str(x+1)])-1} 명", value=f"> **시즌 출첵횟수**: **`{top_dic[str(x+1)][0][1]}`**회")
            elif len(top_dic[str(x+1)]) == 1:
                if (x + 1) == 1:
                    top1_message = f"**{self.bot.get_user(top_dic[str(x+1)][0][0])}**님"
                emb.add_field(name=f"{text} {self.bot.get_user(top_dic[str(x+1)][0][0])}",
                              value=f"> **시즌 출첵횟수**: **`{top_dic[str(x+1)][0][1]}`**회\n> **전체 출첵횟수**: **`{top_dic[str(x+1)][0][2]}`**회")
            if (x + 1) % 2 == 1:
                emb.add_field(name="\u200b", value="\u200b", inline=True)
        emb.set_footer(text="갱신 주기: 60s")
        await msg.edit(embed=emb, content=f"🎊 {top1_message} 1등 축하드립니다. 🎊")

    def load_data(self, user_id):
        conn = sqlite3.connect(
            "database/User_Data/check.db", isolation_level=None)
        c = conn.cursor()
        c.execute("SELECT * FROM attendancecheck WHERE id='%s'" % user_id)
        return_value = c.fetchone()
        return return_value

    @commands.Cog.listener(name="on_message")
    async def attendance_check(self, message):
        if message.channel.id == 785850711316496426 and not message.author.bot:
            await message.delete()
            user_roles = []
            for i in message.author.roles:
                user_roles.append(str(i))
            conn = sqlite3.connect(
                "database/User_Data/check.db", isolation_level=None)
            c = conn.cursor()
            c.execute(f"CREATE TABLE IF NOT EXISTS attendancecheck(id integer PRIMARY KEY not null, season_check integer not null, ad_check integer not null, lastday integer not null, top1 integer not null)")
            conn.commit()
            u_data = self.load_data(message.author.id)
            lastday = int((datetime.datetime.now()).strftime("%Y%m%d"))
            with open('./database/User_Data/attendance_check.json', 'r') as f:
                data = json.load(f)
            if u_data is None:
                u_ad_check = 0
                u_season_check = 0
                u_lastday = 0
                u_top1 = 0
                c.execute("INSERT INTO attendancecheck(id, season_check, ad_check, lastday, top1) VALUES(?,?,?,?,?)",
                          (message.author.id, u_season_check, u_ad_check, u_lastday, u_top1))
            elif u_data is not None:
                u_ad_check = u_data[2]
                u_season_check = u_data[1]
                u_lastday = u_data[3]
                u_top1 = u_data[4]
                if u_lastday == lastday:
                    return await message.author.send(embed=self.check_i(message.author, message), content=message.author.mention)
            c.execute("UPDATE attendancecheck SET season_check = ?, ad_check = ?, lastday = ? WHERE id = ?",
                      (u_season_check+1, u_ad_check+1, lastday, message.author.id))
            for role in data["reward"]:
                r_rs = int((list(role.keys()))[0])
                if r_rs <= (u_ad_check+1):
                    if str(discord.utils.get(message.guild.roles, id=role[str(r_rs)])) not in user_roles:
                        await message.author.add_roles(discord.utils.get(message.guild.roles, id=role[str(r_rs)]))
                elif r_rs > (u_ad_check+1):
                    break
            now = datetime.datetime.now()
            emb = discord.Embed(color=random.randint(0, 0xffffff))
            emb.set_author(
                name=f"안녕하세요! {message.author.name}님", icon_url=message.author.avatar_url)
            emb.add_field(name="🏆 **내 순위:**",
                          value=f"**`{len(message.guild.members)}`명 중 `처리중...`위**")
            emb.add_field(name="📅 **시즌/전체 출첵 횟수:**",
                          value=f"**`{u_season_check+1}`/`{u_ad_check+1}`번**")
            emb.add_field(name="🕒 **출첵 시간:**", value=now.strftime(
                "`%Y. %m. %d` **`%p %I:%M`**").replace('PM', '오후').replace('AM', '오전'), inline=False)
            emb.set_footer(text=f"오늘의 멘트: {message.content}")
            msg = await message.channel.send(embed=emb, content=message.author.mention)
            await self.daily_rank(msg)

    @commands.command(name="checkinfo", aliases=["checki"])
    @commands.has_permissions(administrator=True)
    async def _checki(self, message, user: discord.Member):
        await message.send(embed=self.check_i(user, message))

    @commands.command(name="checkwarn", aliases=["checkw"])
    @commands.has_permissions(administrator=True)
    async def _checkw(self, message, message_id: int, *, warn_message: str = "검거된 메세지 입니다."):
        msg = await self.bot.get_channel(785850711316496426).fetch_message(message_id)
        msg_emb_data = msg.embeds[0]
        msg_content_data = msg.mentions[0]
        emb = discord.Embed(color=msg_emb_data.color)
        emb.set_author(name=msg_emb_data.author.name,
                       icon_url=msg_emb_data.author.icon_url)
        for f in msg_emb_data.fields:
            emb.add_field(name=f.name, value=f.value, inline=f.inline)
        emb.set_footer(text=msg_emb_data.footer.text)
        await msg_content_data.send(embed=emb, content=f"{msg_content_data.mention} 최근 출첵을 하신 메세지가 검거되었습니다.\n> 사유: {warn_message}")
        emb.set_footer(text=f"오늘의 멘트: 검거된 메세지 입니다.")
        await msg.edit(embed=emb, content=msg_content_data.mention)
        await message.reply(f"> `{msg_emb_data.footer.text.replace('오늘의 멘트: ', '')[0:20]}`\n를/(을) 검거하였습니다.")

    @commands.command(name="checkrank", aliases=["checkr"])
    @commands.has_permissions(administrator=True)
    async def _checkr(self, message):
        await message.reply("순위를 재설정 합니다.")
        guild = message.guild
        day_messages = []
        channel = self.bot.get_channel(785850711316496426)
        nowday = int((datetime.datetime.now()).strftime("%Y%m%d"))
        async for message in channel.history(limit=len(guild.members)):
            if int((message.created_at + datetime.timedelta(hours=9)).strftime("%Y%m%d")) == nowday and len(message.embeds) > 0:
                day_messages.append(message)
        for i, x in enumerate(day_messages):
            msg_emb_data = x.embeds[0]
            emb = discord.Embed(color=msg_emb_data.color)
            emb.set_author(name=msg_emb_data.author.name,
                           icon_url=msg_emb_data.author.icon_url)
            for f in msg_emb_data.fields:
                value = f.value
                if f.name == "🏆 **내 순위:**":
                    value = f"**`{len(guild.members)}`명 중 `{len(day_messages) - i}`위**"
                emb.add_field(name=f.name, value=value, inline=f.inline)
            emb.set_footer(text=msg_emb_data.footer.text)
            await x.edit(embed=emb)


def setup(bot):
    bot.add_cog(attendance_check(bot))
