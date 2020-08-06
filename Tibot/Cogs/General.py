import asyncio
import discord
import global_storage as gs #pylint: disable=import-error

from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")
    


