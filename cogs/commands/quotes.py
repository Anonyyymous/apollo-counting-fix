from utils.MaybeMention import MaybeMention
from datetime import datetime
import logging

from discord.ext import commands
from discord.ext.commands import Bot, Context, clean_content
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import ScalarListException

from models import Quote, db_session
from utils import (
    get_database_user,
    get_database_user_from_id,
    get_name_string,
    user_is_irc_bot,
)

LONG_HELP_TEXT = """
Record, edit, and delete quotes. Quotes may also be randomly drawn or queried by ID number. You may also opt out of being quoted.
"""
SHORT_HELP_TEXT = """Record and manage quotes attributed to authors"""


class Quotes(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.group(help=LONG_HELP_TEXT, brief=SHORT_HELP_TEXT)
    async def quote(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send("Subcommand not found.")

    @quote.command(help="Add a quote, format !quote add <author> <quote text>.")
    async def add(self, ctx: Context, author: MaybeMention, *, quote_text: str):
        submitter_type = "id"
        author_type = "id"
        now = datetime.now()

        # get the submitter's id/name
        display_name = get_name_string(ctx.message)

        if user_is_irc_bot(ctx):
            submitter_type = "string"
            submitter_id = None
            submitter_string = display_name
        else:
            submitter_id = get_database_user(ctx.author).id
            submitter_string = None

        # get the mentioned user's id/name
        if isinstance(author, str):
            author_type = "string"
            author_id = None
            author_string = author
        else:
            author_id = author.id
            author_string = None

        new_quote = Quote(
            submitter_type=submitter_type,
            submitter_id=submitter_id,
            submitter_string=submitter_string,
            author_type=author_type,
            author_id=author_id,
            author_string=author_string,
            quote=quote_text,
            created_at=now,
            edited=False,
            edited_at=None,
        )
        db_session.add(new_quote)
        try:
            db_session.commit()
            await ctx.send(
                f"Thanks {display_name}, I have saved this quote with the ID {new_quote.quote_id}."
            )
        except (ScalarListException, SQLAlchemyError) as e:
            db_session.rollback()
            logging.exception(e)
            await ctx.send(f"Something went wrong")


def setup(bot: Bot):
    bot.add_cog(Quotes(bot))
