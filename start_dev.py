from debug_utils import print_exception
from discord.ext.commands import ExtensionNotLoaded
from asyncio import sleep, get_event_loop
from start import start, async_init, bot, load_extension, unload_extension
from check_changes import check_changes

async def start_dev_env():
    while True:
        changes = check_changes('modules')
      # changes = [ [changed], [added], [removed] ]
        if sum(changes, []):
            # changed
            for file in changes[0]:
                file = file.rsplit('.py', 1)[0]
                try:
                    unload_extension('modules.' + file)
                    load_extension('modules.' + file)
                    await async_init(file)
                except ExtensionNotLoaded:
                    load_extension('modules.' + file)
                    await async_init(file)
                except Exception as error:
                    print_exception(error)
                print("Reloaded '{}'".format(file.replace('.', ' ')))
            # added
            for file in changes[1]:
                file = file.rsplit('.py', 1)[0]
                try:
                    load_extension('modules.' + file)
                    await async_init(file)
                except Exception as error:
                    print_exception(error)
                print("Loaded '{}'".format(file.replace('.', ' ')))
            # removed
            for file in changes[2]:
                file = file.rsplit('.py', 1)[0]
                unload_extension('modules.' + file)
                print("Unloaded '{}'".format(file.replace('.', ' ')))
        await sleep(1)

if __name__ == '__main__':
    get_event_loop().create_task(start_dev_env())
    print('Dev Environment Active')
    start()