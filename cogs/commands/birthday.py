from datetime import datetime

from discord import User
from discord.ext import commands
from discord.ext.commands import Bot, Context
from psycopg import OperationalError
from pytz import timezone, utc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from config import CONFIG
from models import db_session
from models.birthday import Birthday as db_Birthday  # avoid name clash
from models.user import User as db_user
from utils import get_database_user

LONG_HELP_TEXT = """
Hapy birthday!!!!

As is tradtion, wish our dear liege chancellor of the computer a happy birthday
"""


class Birthday(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        recent = db_session.query(db_Birthday).order_by(db_Birthday.date.desc()).first()
        if recent:  # store the most recent birthday
            self.date = recent.date
            self.age = recent.age
        else:  # if there is no birthday, initialise
            self.date = utc.localize(datetime(1970, 1, 1)).astimezone(
                timezone("Europe/London")
            )
            self.age = 0

    @commands.hybrid_group(help=LONG_HELP_TEXT, brief="HAPPY BIRTHDAY!!!!")
    async def birthday(self, ctx: Context):
        await self.wish(ctx)

    @birthday.command(help=LONG_HELP_TEXT, brief="HAPPY BIRTHDAY!!!!")
    async def wish(self, ctx: Context):
        """Adds 1 to the age of the Liege Chancellor and wishes them a happy birthday"""
        first = False
        current_date = utc.localize(datetime.now()).astimezone(
            timezone("Europe/London")
        )  # gets the current date
        if current_date.date() > self.date.date():
            try:
                self.date = current_date
                self.age += 1
                first = True
                db_user = get_database_user(ctx.author)
                borth = db_Birthday(date=self.date, age=self.age, user_id=db_user.id)
                db_session.add(borth)
                db_session.commit()
            except (SQLAlchemyError, OperationalError):
                pass
        await ctx.reply(
            f"Happy birthday <@{CONFIG.LIEGE_CHANCELLOR_ID}>!!!!! <:ferris_party:1016463393156247623> {f' You are now {self.age} years old' if first else ''}"
        )

    @birthday.command(help=LONG_HELP_TEXT, brief="Liege Chancellor age")
    async def age(self, ctx: Context):
        """Get the current age of the Liege Chancellor"""
        name = self.bot.get_user(CONFIG.LIEGE_CHANCELLOR_ID).name
        await ctx.reply(f"{name} is {self.age}")

    @birthday.command(help=LONG_HELP_TEXT, brief="User happy birthday count")
    async def user(self, ctx: Context, user: User):
        """How many times has someone wished the Liege Chancellor a happy birthday?"""
        db_user = get_database_user(user)
        num = (
            db_session.query(db_Birthday)
            .filter(db_Birthday.user_id == db_user.id)
            .count()
        )
        await ctx.reply(
            f"{user.name} has wished the Liege Chancellor a happy birthday {num} times"
        )

    @birthday.command(help=LONG_HELP_TEXT, brief="leaderboard")
    async def leaderboard(self, ctx: Context):
        """Who has wished the Liege Chancellor a happy birthday the most?"""
        leaderboard = (
            db_session.query(db_Birthday.user_id, func.count(db_Birthday.user_id))
            .group_by(db_Birthday.user_id)
            .order_by(func.count(db_Birthday.user_id).desc())
            .all()
        )
        leaderboard_users = ""
        for i in range(5):
            if i >= len(leaderboard):
                break
            user = leaderboard[i]
            user_name = self.bot.get_user(
                db_session.query(db_user)
                .filter(db_user.id == user.user_id)
                .first()
                .user_uid
            ).name
            num_wishes = user[1]
            leaderboard_users += f"\n{i+1}. {user_name} with {num_wishes} wish{'' if num_wishes == 1 else 'es'}"
        # for anyone that cares this can be done in one line: leaderboard_users = "\n".join([f"{i+1}. {self.bot.get_user(db_session.query(db_user).filter(db_user.id == user.user_id).first().user_uid).name} with {user[1]} wish{'' if user[1] == 1 else 'es'}" for i, user in enumerate(leaderboard[:5])]
        await ctx.reply(f"Leaderboard:{leaderboard_users}")


async def setup(bot: Bot):
    await bot.add_cog(Birthday(bot))
