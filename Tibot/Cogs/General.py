import ast
import asyncio
import discord
import global_storage as gs #pylint: disable=import-error

from discord.ext import commands

def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)
    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)
    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.AsyncWith):
        insert_returns(body[-1].body)

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        userdata = gs.USERDATA_READ(member.id)
        welcome_channel = self.bot.get_channel(gs.WELCOME_CHANNEL)
        if userdata["code"] == None:
            userdata["code"] = gs.CREATECODE()
            gs.USERDATA_WRITE(member.id, userdata)
        await welcome_channel.send(f"Welcome {member.mention} to Tibot Support! We're glad to have you. Please make sure to read the rules.")
        if not member.bot:
            member_role = member.guild.get_role(gs.DEFAULT_ROLE)
            await member.add_roles(member_role)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if message.channel.id != gs.COUNTING_CHANNEL: return
        
        counting_channel = message.channel
        counting_lastnumber = "counting_lastnumber.txt"
        counting_lastuser = "counting_lastuser.txt"
        
        last_user = gs.FILEREAD(counting_lastuser)
        gs.FILEWRITE(counting_lastuser, str(message.author.id))
        
        n = int(gs.FILEREAD(counting_lastnumber))
        nn = n + 1
        print(nn)

        if message.content.startswith(str(nn)) != True:
            await counting_channel.send(f"The next number was {nn}. Restarting at 1.")
            gs.FILEWRITE(counting_lastuser, "0")            
            return gs.FILEWRITE(counting_lastnumber, "0")
        
        if str(message.author.id) == last_user:
            await counting_channel.send(f"You can't send two numbers in a row. The next number was {nn}. Restarting at 1.")
            gs.FILEWRITE(counting_lastuser, "0")
            return gs.FILEWRITE(counting_lastnumber, "0")            
        await message.add_reaction("✅")
        gs.FILEWRITE(counting_lastnumber, str(nn))
        
    @commands.command(aliases = ["eval"])
    @commands.is_owner()
    async def evaluate(self, ctx, *, cmd):
        fn_name = "_eval_expr"
        cmd = cmd.strip("` ")
        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body
        insert_returns(body)
        env = {'bot': self.bot, 'discord': discord, 'commands': commands, 'ctx': ctx, '__import__': __import__, "gs": gs}
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
        result = (await eval(f"{fn_name}()", env))
        await ctx.send(result)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")
    


