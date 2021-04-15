# pylint: disable=no-member

import discord
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
        self.top_dic = {}

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

    @commands.Cog.listener()
    async def on_ready(self):
        self.attendance_check_top.start()
        self.attendance_check_sesaon.start()

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
            v.sort(key=lambda x: -x[1])
            v_check = 0
            top_u = []
            for t in v:
                if v_check <= t[1]:
                    top_u.append(self.bot.get_user(t[0]).mention)
                    v_check = t[1]
                else:
                    break
            for u in v:
                c.execute(
                    "UPDATE attendancecheck SET season_check = ? WHERE id = ?", (0, u[0]))
            await self.bot.get_channel(640032706058649642).send(
                "> **시즌이 변경되었습니다.**\n"
                f"**{data['season']['season_name']} 시즌**에서 **{data['season']['season_name']+1} 시즌**으로 변경되었습니다.\n**자 이제 모두 불타오르세요!**\n\n"
                "> 시즌이 변경되어 모든 시즌 출첵 횟수가 초기화 되었습니다.\n\n"
                f"**{data['season']['season_name']} 시즌** 1위: " +
                " ,".join(top_u)
            )
            data["season"]["season_name"] += 1
            data["season"]["startday"] = nowday
            with open('./database/User_Data/attendance_check.json', 'w') as f:
                json.dump(data, f, indent=4)

    @tasks.loop(seconds=1)
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
        msg = await self.bot.get_channel(826025817569099786).fetch_message(826026211288416337)
        emb = discord.Embed(
            title=f"**{data['season']['season_name']} 시즌**", timestamp=datetime.datetime.utcnow())
        for x in v:
            if self.bot.get_user(x[0]) is None:
                c.execute(
                    "DELETE FROM attendancecheck WHERE id = ?", (int(x[0])))
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
            rtop = discord.utils.get(
                message.guild.roles, id=825296383971688459)
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
                    rank = int(self.rank_check(message.author.id))
                    for role in data["reward"]:
                        r_rs = int((list(role.keys()))[0])
                        if r_rs > (u_ad_check):
                            role_name = str(discord.utils.get(
                                message.guild.roles, id=role[str(r_rs)]))
                            break
                    emb = discord.Embed(timestamp=datetime.datetime.utcnow())
                    emb.add_field(name="> **전체 출첵횟수**",
                                  value=f"**`{u_ad_check}`**회")
                    emb.add_field(name="> **시즌 출첵횟수**",
                                  value=f"**`{u_season_check}`**회")
                    emb.add_field(
                        name="> 다음 등급", value=f"{role_name} 까지 `{r_rs - u_ad_check}`회 남았습니다.", inline=False)
                    emb.description = f"**시즌 순위**: **`{rank}`등**"
                    return await message.author.send(embed=emb, content=message.author.mention)
            if lastday != data["day"]:
                await message.guild.get_member(data["top"]).remove_roles(rtop)
                await message.author.add_roles(rtop)
                c.execute("UPDATE attendancecheck SET top1 = ? WHERE id = ?",
                          (u_top1+1, message.author.id))
                data["day"] = lastday
                data["count"] = 0
                data["top"] = int(message.author.id)
            data["count"] += 1
            with open('./database/User_Data/attendance_check.json', 'w') as f:
                json.dump(data, f, indent=4)
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
                          value=f"**`{len(message.guild.members)}`명 중 `{data['count']}`위**")
            emb.add_field(name="📅 **시즌/전체 출첵 횟수:**",
                          value=f"**`{u_season_check+1}`/`{u_ad_check+1}`번**")
            emb.add_field(name="🕒 **출첵 시간:**", value=now.strftime(
                "`%Y. %m. %d` **`%p %I:%M`**").replace('PM', '오후').replace('AM', '오전'), inline=False)
            emb.set_footer(text=f"오늘의 멘트: {message.content}")
            await message.channel.send(embed=emb, content=message.author.mention)

    @ commands.command(name="출첵복구")
    @ commands.is_owner()
    async def _is_onw(self, message, u_id: discord.Member, ad_check: int):
        conn = sqlite3.connect(
            "database/User_Data/check.db", isolation_level=None)
        c = conn.cursor()
        c.execute("UPDATE attendancecheck SET ad_check = ?, lastday = ? WHERE id = ?",
                  (ad_check, 0, message.author.id))
        await message.send("완료")


def setup(bot):
    bot.add_cog(attendance_check(bot))
