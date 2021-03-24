import discord
import sys
from discord.ext import commands
from os import environ, listdir
from debug_utils import print_exception
from importlib import import_module, reload
from inspect import getmembers, isclass

# Configuration #

prefix = '/'
status_message = 'Mention Me!'
module_blacklist = []#['Example']

# Configuration End #

bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), intents=discord.Intents.all())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

init = False
@bot.listen('on_ready')
async def on_ready():
    global init
    await bot.change_presence(activity=discord.Game(name=status_message))
    if not init:
        init = True
        await async_init()
        print("\nLoaded Modules: [{}] ".format(len(bot.cogs.keys())) + ', '.join([cog.replace('_', ' ') for cog in bot.cogs.keys()]))
        server_list = [server.name for server in bot.guilds]
        print("\nConnected Servers: [{}] ".format(str(len(server_list))) + ', '.join(server_list))

async def async_init(cog=None):
    if cog:
        cogs = [bot.cogs[cog]]
    else:
        cogs = bot.cogs.values()
    for cog in cogs:
        try:
            cog.bot = bot
            await cog.__asinit__()
        except AttributeError:
            pass
        except TypeError as e:
            pass
        except Exception as error:
            print_exception(error)

def unload_extension(filename):
    extension = import_module(filename)
    cog_type = type(commands.Cog)
    for obj in getmembers(extension, isclass):
        cog = obj[1]
        if isinstance(cog, cog_type):
            bot.remove_cog(cog.__cog_name__)
            reload(extension)

@timer
def load_extension(filename):
    extension = import_module(filename)
    cog_type = type(commands.Cog)
    for obj in getmembers(extension, isclass):
        cog = obj[1]
        if isinstance(cog, cog_type):
            cog.prefix = prefix
            cog.bot = bot
            try:
                bot.add_cog(cog())
            except Exception as error:
                print(error)

def start():
    bot.remove_command('help')
    files = [file.rsplit('.py', 1)[0] for file in listdir('modules') if file.endswith('.py') and file.rsplit('.py', 1)[0] not in module_blacklist]
    for file in files:
        load_extension('modules.' + file)
    load_extension('Help')
    print('\nLogging in...')
    try:
        if len(sys.argv) > 1:
            token = sys.argv[1]
        else:
            token = environ['BOT_TOKEN']
        bot.run(token)
    except discord.errors.LoginFailure:
        input("Invalid bot token.")
        return
    except KeyError:
        input("Invalid bot token.")
        return

if __name__ == '__main__':
    start()