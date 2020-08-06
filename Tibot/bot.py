import discord

import Cogs #pylint: disable=import-error
import global_storage as gs #pylint: disable=import-error

from discord.ext import commands

class Tibot(commands.Bot):
    async def on_ready(self):
        print("LOAD")
        await bot.change_presence(activity = discord.Activity(name = "the world go round", type = discord.ActivityType.watching))

    async def on_message(self, message):
        if message.author.bot: return
        return await bot.process_commands(message)    

bot = Tibot(command_prefix = gs.PREFIX)
bot.add_cog(Cogs.General(bot))
bot.add_cog(Cogs.Tickets(bot))
bot.run(gs.FILEREAD("token"))
