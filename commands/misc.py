from discord.ext import commands
from discord.ext.commands import Context, Bot

ZED0_HELP_TEXT = """Very important command."""
FAUX_HELP_TEXT = """A member of the Rust evangelical strike force."""
GO_HELP_TEXT = """The eternal #cs meme."""
DUNNO_HELP_TEXT = """¯\\_(ツ)_/¯"""
RUST_HELP_TEXT = """And if you gaze long into RUST, the RUST also gazes into you."""
PR_HELP_TEXT = """You know what to do"""


class Misc:
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(help=ZED0_HELP_TEXT, brief=ZED0_HELP_TEXT)
    async def zed0(self, ctx: Context):
        await ctx.send("¬_¬")

    @commands.command(help=FAUX_HELP_TEXT, brief=FAUX_HELP_TEXT)
    async def faux(self, ctx: Context):
        await ctx.send("RUST")

    @commands.command(help=GO_HELP_TEXT, brief=GO_HELP_TEXT)
    async def go(self, ctx: Context):
        await ctx.send("lol no generics")

    @commands.command(help=DUNNO_HELP_TEXT, brief=DUNNO_HELP_TEXT)
    async def dunno(self, ctx: Context):
        await ctx.send("¯\\_(ツ)_/¯")

    @commands.command(help=RUST_HELP_TEXT, brief=RUST_HELP_TEXT)
    async def rust(self, ctx: Context):
        await ctx.send("FAUX")
        
    @commands.command(help=PR_HELP_TEXT, brief=PR_HELP_TEXT)
    async def pr(self, ctx: Context):
        await ctx.send("You can make a pull request for that!")


def setup(bot: Bot):
    bot.add_cog(Misc(bot))