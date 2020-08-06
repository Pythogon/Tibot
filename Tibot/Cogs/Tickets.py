import asyncio
import discord
import global_storage as gs #pylint: disable=import-error

from discord.ext import commands

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    @commands.Cog.listener()
    async def on_message(self, message):
        code = gs.USERDATA_READ(message.author.id)["code"]
        if message.author.bot: return
        if message.content.startswith(gs.PREFIX): return
        pair = gs.QUERY_PAIR(message.channel.id)
        if pair == None: return
        content = message.content
        for attachment in message.attachments:
            content += f"\n{attachment.url}"
        tunnel = self.bot.get_channel(pair)
        await tunnel.send(f"[{code}] ○:tropical_fish:● {content}")
        await message.channel.edit(topic=message.author.id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        userdata = gs.USERDATA_READ(member.id)
        welcome_channel = self.bot.get_channel(gs.WELCOME_CHANNEL)
        if userdata["code"] == None:
            userdata["code"] = gs.CREATECODE()
            gs.USERDATA_WRITE(member.id, userdata)
        await welcome_channel.send(f"Welcome {member.mention} to Tibot Support! We're glad to have you. Please make sure to read the rules.")
    
    @commands.command()
    async def close(self, ctx):
        ticketid = int(ctx.channel.name)
        tickets = gs.JSONREAD("channel_pairs.json")
        to_pop = None
        for x in range(len(tickets)):
            element = tickets[x]
            if element[0] == ticketid:
                server_channel = self.bot.get_channel(element[0])
                await server_channel.send("Ticket closed, this channel will be locked in 10 seconds.")
                user_channel = self.bot.get_channel(element[1])
                await user_channel.send("Ticket closed, this channel will be locked in 10 seconds.")
                await asyncio.sleep(10)
                if user_channel.topic in gs.NO_LOGS:
                    await server_channel.delete()
                else:
                    await server_channel.edit(overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)}, category = self.bot.get_channel(gs.TICKET_CATEGORY_COMPLETE))
                await user_channel.delete()
                to_pop = x
            
        if to_pop == None:
            return await ctx.send("I couldn't find any ticket with that ID.")
        else:
            tickets.pop(to_pop)
            gs.JSONWRITE("channel_pairs.json", tickets)  

    @commands.group()
    @commands.has_role(740322815227592727)
    async def notes(self, ctx):
        if ctx.invoked_subcommand == None:
            await ctx.send("Correct usage is ~`notes add|list|remove`")

    @notes.command(name = "add")
    async def notes_add(self, ctx, code, *note):
        note = " ".join(note)
        with open(f"local_Store/notes/{code}", "a+") as file:
            file.write(f"{note}\n")
        await ctx.send("Added note.")

    @notes.command(name = "list")
    async def notes_list(self, ctx, code):
        with open(f"local_Store/notes/{code}", "r") as file:
            data = file.read()
            data = data.split("\n")
        to_send = ""
        for x in range(len(data)):
            to_send += f"`{x+1}`: {data[x]}\n"
        await ctx.send(to_send)
    
    @notes.command(name = "remove")
    async def notes_remove(self, ctx, code, number: int):
        with open(f"local_Store/notes/{code}", "r") as file:
            data = file.read()
            data.split("\n")
        data.pop(number - 1)
        data = "\n".join(data)
        with open(f"local_Store/notes/{code}", "w") as file:
            file.write(data)
        await ctx.send("Removed note.")

    @commands.command()
    async def notify(self, ctx):
        try:
            tunnel = self.bot.get_channel(gs.QUERY_PAIR(ctx.channel.id))
            tunnel_user = self.bot.get_user(int(tunnel.topic))
            await tunnel.send(tunnel_user.mention)
        except: pass
        
    @commands.command()
    async def support(self, ctx):
        author = ctx.author.id
        member = ctx.guild.get_member(author)
        pairs = gs.JSONREAD("channel_pairs.json")
        server_category = self.bot.get_channel(gs.TICKET_CATEGORY_CONTROL)
        user_category = self.bot.get_channel(gs.TICKET_CATEGORY_USER)
        userdata = gs.USERDATA_READ(author)
        code = userdata["code"]
        if code == None:
            code = gs.CREATECODE()
            userdata["code"] = code
            gs.USERDATA_WRITE(author, userdata)

        server_overwrites = {ctx.guild.get_role(740322815227592727): discord.PermissionOverwrite(read_messages=True, send_messages=True), 
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
        server_channel = await ctx.guild.create_text_channel("holding", category = server_category, overwrites = server_overwrites)
        await server_channel.edit(name = str(server_channel.id))
        await server_channel.send(f"New ticket from {code}.")

        user_overwrites = {member: discord.PermissionOverwrite(read_messages=True, send_messages=True), 
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
        user_channel = await ctx.guild.create_text_channel("holding", category = user_category, overwrites = user_overwrites)
        await user_channel.edit(name = str(server_channel.id))
        await user_channel.send(f"Heya {member.mention}! Thank you for using Tibot. Your ticket number is {server_channel.id}. A representative will be here shortly.")
        
        pairs.append([server_channel.id, user_channel.id])
        gs.JSONWRITE("channel_pairs.json", pairs)
        await ctx.message.delete()