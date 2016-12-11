from discord.ext import commands
from .utils import checks
from __main__ import settings
import os
import discord
import glob
from .utils.chat_formatting import pagify, box
import re
import os
import aiohttp
from random import choice
try:
    import ffmpy
    ffmpyinstalled = True
except:
    ffmpyinstalled = False

class useful:
    """Useful stuffz!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name="avatar", aliases=["av"])
    async def avatar(self, ctx, user : discord.Member):
        if user.avatar_url:
            avatar = user.avatar_url
        else:
            avatar = user.default_avatar_url
        em = discord.Embed(color=discord.Color.red())
        em.add_field(name=user.mention + "'s avatar", value=avatar)
        em.set_image(url=avatar, height="128", width="128")
        await self.bot.say(embed=em)

    @commands.command(pass_context=True, name="calc", aliases=["calculate"])
    async def _calc(self, ctx, evaluation):
        """Solves a math problem so you don't have to!
        + = add, - = subtract, * = multiply, and / = divide

        Example:
        [p]calc 1+1+3*4"""
        prob = re.sub("[^0-9+-/* ]", "", ctx.message.content[len(ctx.prefix + "calc "):].strip())
        try:
            answer = str(eval(prob))
            await self.bot.say("`{}` = `{}`".format(prob, answer))
        except:
            await self.bot.say("I couldn't solve that problem, it's too hard")

    @commands.command(pass_context=True)
    async def suggest(self, ctx, *, suggestion : str):
        """Sends a suggestion to the owner."""
        if settings.owner == "id_here":
            await self.bot.say("I have no owner set, cannot suggest.")
            return
        owner = discord.utils.get(self.bot.get_all_members(), id=settings.owner)
        author = ctx.message.author
        if ctx.message.channel.is_private is False:
            server = ctx.message.server
            source = "server **{}** ({})".format(server.name, server.id)
        else:
            source = "direct message"
        sender = "**{}** ({}) sent you a suggestion from {}:\n\n".format(author, author.id, source)
        message = sender + suggestion
        try:
            await self.bot.send_message(owner, message)
        except discord.errors.InvalidArgument:
            await self.bot.say("I cannot send your message, I'm unable to find"
                               " my owner... *sigh*")
        except discord.errors.HTTPException:
            await self.bot.say("Your message is too long.")
        except:
            await self.bot.say("I'm unable to deliver your message. Sorry.")
        else:
            await self.bot.say("Your message has been sent.")

    @commands.command(pass_context=True)
    async def botowner(self, ctx):
        """Shows you who's boss!"""
        await self.bot.say("My owner is <@{}>.".format(settings.owner))

    @commands.command(pass_context=True)
    async def saytts(self, ctx, *, msg):
        """Sends a message with text to speech."""
        try:
            await self.bot.send_message(ctx.message.channel, tts=True, content=msg)
        except discord.Forbidden:
            await self.bot.say("Can't send tts message.")

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        """Sends you a link to invite the bot to your server."""
        url = discord.utils.oauth_url(self.bot.user.id)
        self.bot.oauth_url = url
        await self.bot.say(""
        "{}, to invite the bot to your server use this link:\n"
        "{}&permissions=-1"
        "\n**BEWARE** You need the 'manage server' permission to add bots.".format(ctx.message.author.mention, url))

    @commands.command(pass_context=True)
    async def genoauth(self, ctx, client_id:int, perms=None):
        """Generates an oauth url (aka invite link) for your bot, for permissions goto https://discordapi.com/permissions.html. Or just put 'all' or 'admin'."""
        url = discord.utils.oauth_url(client_id)
        if perms == "all":
            await self.bot.say(""
            "{}, here you go:\n"
            "{}&permissions=-1".format(ctx.message.author.mention, url))
        elif perms == "admin":
            await self.bot.say(""
            "{}, here you go:\n"
            "{}&permissions=8".format(ctx.message.author.mention, url))
        elif perms:
            await self.bot.say(""
            "{}, here you go:\n"
            "{}&permissions={}".format(ctx.message.author.mention, url, perms))
        else:
            await self.bot.say(""
            "{}, here you go:\n"
            "{}".format(ctx.message.author.mention, url))

    @commands.command(pass_context=True)
    async def genbotoauth(self, ctx, bot:discord.Member, perms=None):
        """Generates an oauth url (aka invite link) for your bot.
        For permissions goto https://discordapi.com/permissions.html. Or just put 'all' or 'admin'.
        Doesn't always work"""
        url = discord.utils.oauth_url(bot.id)
        if not bot.bot:
            await self.bot.say("User is not a bot.")
            return
        if perms == "all":
            await self.bot.say(""
            "{}, here you go:\n"
            "{}&permissions=-1".format(ctx.message.author.mention, url))
        elif perms == "admin":
            await self.bot.say(""
            "{}, here you go:\n"
            "{}&permissions=8".format(ctx.message.author.mention, url))
        elif perms:
            await self.bot.say(""
            "{}, here you go:\n"
            "{}&permissions={}".format(ctx.message.author.mention, url, perms))
        else:
            await self.bot.say(""
            "{}, here you go:\n"
            "{}".format(ctx.message.author.mention, url))

    @checks.mod_or_permissions()
    @commands.command(pass_context=True)
    async def uploadcog(self, ctx, cogname):
        """Uploads a cog for you to use, for a list of cogs use [p]show_cogs"""
        await self.bot.say("Here you go:")
        await self.bot.send_file(ctx.message.channel, fp="cogs/{}.py".format(cogname), filename="{}.py".format(cogname))

    # copied from the owner cog since the command there was owner only and here it isn't :3
    @checks.mod_or_permissions()
    @commands.command()
    async def show_cogs(self):
        """Shows loaded/unloaded cogs"""
        loaded = [c.__module__.split(".")[1] for c in self.bot.cogs.values()]
        unloaded = [c.split(".")[1] for c in self._list_cogs()
                    if c.split(".")[1] not in loaded]
        if not unloaded:
            unloaded = ["None"]
        msg = ("+ Loaded\n{}\n\n- Unloaded\n{}".format(", ".join(sorted(loaded)), ", ".join(sorted(unloaded))))
        for page in pagify(msg, [" "], shorten_by=16):
            await self.bot.say(box(page.lstrip(" "), lang="diff"))

    @commands.command()
    async def discrim(self, discriminator: str):
        """Shows you all the members I can find with the discrim you gave."""
        discriminator = discriminator.replace("#", "")
        if not discriminator.isdigit():
            await self.bot.say("A Discrimnator can only have digits and a #\nExamples\n`#4157`, `4157`")
            return

        members = [str(s) for s in list(self.bot.get_all_members()) if s.discriminator == discriminator]
        members = ", ".join(list(set(members)))
        if not members:
            await self.bot.say("I could not find any users in any of the servers I'm in with a discriminator of `{}`".format(discriminator))
            return
        else:
            embed = discord.Embed(colour=0X00B6FF)
            embed.add_field(name="Discriminator #{}".format(discriminator), value=str(members), inline=False)
            try:
                await self.bot.say(embed=embed)
            except:
                await self.bot.say("An unknown error occured while embedding.")

    @commands.command()
    async def emoteurl(self, *, emote:discord.Emoji):
        """Gets the url for a CUSTOM emote (meaning no emotes like :eyes: and :ok_hand:)"""
        await self.bot.say(emote.url)

    @commands.command()
    async def showservers(self):
        """Shows you all the servers the bot is in."""
        servers = sorted(list(self.bot.servers), key=lambda s: s.name.lower())
        serversmsg = ""
        for i, server in enumerate(servers):
            serversmsg += "{}: {}\n".format(i+1, server.name)
        await self.bot.say("I am currently in\n" + serversmsg)

    @commands.command()
    async def servercount(self):
        """Shows you in how many servers the bot is."""
        stats = await self.bot.say("Getting stats, this may take a while.")
        uniquemembers = []
        for member in list(self.bot.get_all_members()):
            if member.name not in uniquemembers:
                uniquemembers.append(member.name)
        await self.bot.edit_message(stats, "I am currently in **{}** servers with **{}** members of which **{}** unique.".format(len(self.bot.servers), len(list(self.bot.get_all_members())), len(uniquemembers)))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60)
    async def bugreport(self, ctx, *, bug:str):
        """Report a bug in the bot."""
        if settings.owner == "id_here":
            await self.bot.say("I have no owner set, cannot report the bug.")
            return
        owner = discord.utils.get(self.bot.get_all_members(), id=settings.owner)
        author = ctx.message.author
        if ctx.message.channel.is_private is False:
            server = ctx.message.server
            source = "server **{}** (`{}`)".format(server.name, server.id)
        else:
            source = "direct message"
        sender = "**{0}** (`{0.id}`) sent you a bug report from {1}:\n\n".format(author, source)
        message = sender + bug
        try:
            await self.bot.send_message(owner, message)
        except discord.errors.InvalidArgument:
            await self.bot.say("I cannot send your bug report, I'm unable to find my owner... *sigh*")
        except discord.errors.HTTPException:
            await self.bot.say("Your bug report is too long.")
        except:
            await self.bot.say("I'm unable to deliver your bug report. Sorry.")
        else:
            await self.bot.say("Your bug report has been sent.")

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60)
    async def convert(self, ctx, file_url:str, input_format:str, output_format:str):
        """Convert a video or audio file to anything you like
        correct output formats would be mp4, mp3, wav, that kind of stuff.

        Input format has to be the same as the input format of the file_url."""
        convertmsg = await self.bot.say("Setting up...")
        number = ''.join([choice('0123456789') for x in range(6)])
        input = "data/useful/{}.{}".format(number, input_format)
        output = "data/useful/{}.{}".format(number, output_format)
        outputname = "{}.{}".format(number, output_format)
        try:
            async with aiohttp.get(file_url) as r:
                file = await r.content.read()
            with open(input, 'wb') as f:
                f.write(file)
        except:
            await self.bot.edit_message(convertmsg, "Could not download the file.")
            try:
                os.remove(input)
            except:
                pass
            return
        try:
            converter = ffmpy.FFmpeg(inputs={input: None}, outputs={output: None})
            await self.bot.edit_message(convertmsg, "Converting...")
            converter.run()
        except:
            await self.bot.edit_message(convertmsg, "Could not convert your file, an error occured.")
            try:
                os.remove(input)
                os.remove(output)
            except:
                pass
            return
        await self.bot.send_file(ctx.message.channel, content="Convertion done!", fp=ouput, filename=outputname)
        await self.bot.delete_message(convertmsg)
        os.remove(input)
        os.remove(output)
        
    @checks.mod_or_permissions()
    @commands.command(pass_context=True)
    async def showservermembers(self, ctx):
        """Lists all the members of a server."""
        servers = sorted(list(self.bot.servers), key=lambda s: s.name.lower())
        msg = ""
        for i, server in enumerate(servers):
            msg += "{}: {}\n".format(i, server.name)
        msg += "\nTo show a servers members just type its number."
        for page in pagify(msg, ['\n']):
            await self.bot.say(page)
        while msg is not None:
            msg = await self.bot.wait_for_message(author=ctx.message.author, timeout=15)
            try:
                msg = int(msg.content)
                await self.show_confirmation(servers[msg], ctx.message.author, ctx)
                break
            except (IndexError, ValueError, AttributeError):
                pass

    async def show_confirmation(self, server, author, ctx):
        await self.bot.say("Are you sure you want to show {}'s members? (yes/no)".format(server.name))
        msg = await self.bot.wait_for_message(author=author, timeout=15)
        if msg is None:
            await self.bot.say("I guess not.")
        elif msg.content.lower() == "yes":
            members = [member.name for member in server.members]
            await self.bot.say("Here you go:\n**{}**.".format("**, **".join(sorted(members))))
        else:
            await self.bot.say("I guess not.")

    def _list_cogs(self):
        cogs = [os.path.basename(f) for f in glob.glob("cogs/*.py")]
        return ["cogs." + os.path.splitext(f)[0] for f in cogs]
        
def check_folders():
    if not os.path.exists("data/useful"):
        print("Creating data/useful folder...")
        os.makedirs("data/useful")
        
class ModuleNotFound(Exception):
    pass
        
def setup(bot):
    if not ffmpyinstalled:
        raise ModuleNotFound("FFmpy is not installed, install it with pip3 install ffmpy")
    check_folders()
    bot.add_cog(useful(bot))