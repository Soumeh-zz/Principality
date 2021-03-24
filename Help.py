from discord import Embed
from discord.ext import commands
from utils import split_every, not_self, module_help, error_message

class Help(commands.Cog):

    # Config #
    
    modules_per_page = 6
    
    # Config End #

    def __init__(self):
        self.command = self.prefix + 'help'
    def __asinit__(self):
        self.bot_mention = '<@!{}>'.format(self.bot.user.id)
        self.modules_dict = dict(self.bot.cogs.items())
        self.modules_dict['Help'] = self
        self.modules = split_every(list(self.modules_dict.keys()), self.modules_per_page)
        self.module_pages = len(self.modules)

    def help_message(self):
        return """Provides help messages for all active modules.\n
``{0} (page)``
 \> View more modules.
``{0} (module)``
 \> Provides help for currently running modules.
""".format(self.command)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == self.bot_mention:
            await self.help_menu(message.channel, 1)

    @commands.command()
    @not_self()
    async def help(self, ctx, *args):
        try:
            message = ctx.message
            channel = message.channel
            if not args:
                return await self.help_menu(channel, 1)
            arg = '_'.join(args)
            if arg.isdigit():
                return await self.help_menu(channel, int(arg))
            else:
                return await self.help_module(channel, arg)
        except Exception as e:
            print(e)

    async def help_menu(self, channel, number):
        if number > 0:
            number -= 1
        if number >= self.module_pages:
            return await error_message(channel, "The number you have entered is too big, it must be at most {}".format(self.module_pages))
        embed = Embed(description="**Modules List - Page {0} out of {1}**\n⠀".format(number + 1, self.module_pages))
        for module in self.modules[number]:
            obj = self.modules_dict[module]
            try:
                desc = obj.help_message()
            except:
                desc = None
            if not desc:
                desc = "This module doesn't have a help message."
            if '\n' in desc:
                desc = desc.split('\n', 1)[0]
            embed.add_field(name=module.replace('_', ' ') + " Module", value=desc, inline=True)
        embed.set_footer(text="⠀\nType {0} (module) for more information on a Module\nType {0} (page) to see more Modules".format(self.command))
        await channel.send(embed=embed)
    async def help_module(self, channel, module_name):
        try:
            if module_name.endswith('_module'):
                module_name = module_name.rsplit('_module', 1)[0]
            for module_obj_name, module_obj in self.modules_dict.items():
                if module_obj_name.lower() == module_name:
                    return await module_help(channel, module_obj)
            await channel.send("Module not found")
        except Exception as e:
            print(e)