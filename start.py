import discord, datetime, asyncio, random, time, os, urllib.request, json, base64, io, aiohttp, requests
from discord.ext import commands
from lxml import html
from PIL import Imagefrom int2ronum import *from insult_generator import *



prefix = '/'

bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return



async def link_to_message(link):
    data = link.split('/channels/')[1].split('/')
    linked_channel = await bot.fetch_channel(int(data[1]))
    return await linked_channel.fetch_message(int(data[2]))

def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randint(int_delta, 0)
    return start + datetime.timedelta(seconds=random_second)

async def react_to_message(message, emoji_list):
    for emoji in emoji_list:
        try:
            await message.add_reaction(emoji)
            await asyncio.sleep(0.3)
        except:
            print("Emoji '{}' not recognized".format(emoji))

async def embed_message(channel, this_message):
    embed_message = this_message.content
    if this_message.content == None:
        raise EmptyMessage("Message is embeded or is a system message")
    if this_message.embeds != []:
        return await message.channel.send("Cannot send Embeded messages (yet).")
    if str(this_message.type) == 'MessageType.pins_add':
        embed_message = "{} pinned a message to this channel. See all the pins.".format(this_message.author.display_name)
    elif str(this_message.type) == 'MessageType.new_member':
        embed_message = "{} Joined the server.".format(this_message.author.display_name)
    this_embed = discord.Embed(description=embed_message + '\n\n[(jump)]({})'.format(this_message.jump_url), timestamp=this_message.created_at)
    this_embed.set_author(url='https://discord.com/users/{}'.format(this_message.author.id), name=this_message.author.name, icon_url=this_message.author.avatar_url)
    this_embed.set_footer(text='#' + this_message.channel.name)
    this_attachment = (this_message.attachments[0:]+[None])[0]
    if this_attachment != None:
        if this_attachment.filename.endswith(('.png', '.gif', '.jpeg', '.jpg')):
            this_embed.set_image(url=this_attachment.url)
        else:
            this_embed.description = this_message.content + f'\n[<{this_attachment.filename}>]({this_attachment.url})\n\n[(jump)]({this_message.jump_url})'
    await channel.send(embed=this_embed)

def EmptyMessage(Exception):
    pass

async def random_message(channel):
    creation_date = channel.created_at
    new_date = random_date(datetime.datetime.now(), creation_date)
    channel_history = channel.history(limit=32, oldest_first=True, after=new_date)
    message_list = await channel_history.flatten()
    if not message_list:
        channel_history = channel.history(limit=32, oldest_first=True, before=new_date)
        message_list = await channel_history.flatten()
    if message_list == []:
        raise IndexError
    this_message = message_list[random.randint(0, len(message_list)-1)]
    return this_message

def not_self():
    def predicate(ctx):
        return ctx.author != bot.user
    return commands.check(predicate)

def get_args(message, command):
    try:
        return message.split(command + ' ')[1]
    except IndexError as e:
        return None

def get_JSON(link):
    content = urllib.request.urlopen(link).read().decode()
    if content == '':
        raise EmptyLinkError
    else:
        return json.loads(content)
        
def EmptyLinkError(Exception):
    pass

async def url_to_file(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            file = io.BytesIO(await resp.read())
            return file
def split_every(list, count):
    return [list[i * count:(i + 1) * count] for i in range((len(list) + count - 1) // count )]

async def module_help(channel, module):
    message = module_map[module]
    if not message:
        return await channel.send("This module does not have a help message")
    embed = discord.Embed(description="**{} Module**".format(module.replace('_', ' ')))
    desc = module_map[module]
    if not desc:
        desc = "This module doesn't have a help message."
    embed.add_field(name='⠀', value=desc, inline=False)
    await channel.send(embed=embed)

# Modules #

class Example(commands.Cog):
    def help_message(self):
        return """Example Module, doesn't do anything.
Another line just for display."""

class Upscale(commands.Cog):
    command = prefix + 'upscale'
    def help_message(self):
        return """Posts an upscaled pixel art image from an attached image.
``{0} (number)``
 \> Upscales an attached image by (a whole number between 2 and 10)""".format(self.command)
    @commands.command()
    @not_self()
    async def upscale(self, ctx):
        message = ctx.message
        arguments = get_args(message.content, self.command)
        if not arguments:
            return await self.InputError(message.channel)
        else:
            try:
                upscale = int(arguments)
                if upscale > 10 or upscale < 2:
                    raise ValueError
            except ValueError:
                return await self.InputError(message.channel)
            try:
                image = message.attachments[0]
                extension = image.filename.rsplit('.')[1]
            except IndexError:
                return await message.channel.send("You must attach an image with this command to upscale it")
            if extension in ['png', 'jpg', 'jpeg']:
                file = await url_to_file(image.proxy_url)
                new_image = Image.open(file)
                new_image = new_image.resize((new_image.size[0] * upscale, new_image.size[1] * upscale), Image.NEAREST)
                new_file = io.BytesIO()
                new_image.save(new_file, 'png')
                new_file.seek(0)
                try:
                    discord_file = discord.File(new_file, filename=image.filename)
                    embed = discord.Embed(description='``{}``'.format(image.filename) + '\nBy <@{}>'.format(message.author.id))
                    embed.set_thumbnail(url=image.proxy_url)
                    embed.set_image(url='attachment://' + image.filename)
                    await message.channel.send(file=discord_file, embed=embed)
                except Exception as e:
                    print(e)
    async def InputError(self, channel):
        await channel.send("Input a whole number between 2 and 10 to upscale the image by")

class Minecraft_Versions(commands.Cog):
    command = prefix + 'mcversion'
    def help_message(self):
        return """Get information about Minecraft's latest releases.
``{0}``
\> Sends a snipper from the wiki page of the latest version of Minecraft.
``{0} (version)``
\> Sends a snippet from the wiki page of a (specified version) of Minecraft.""".format(self.command)
    @commands.command()
    @not_self()
    async def mcversion(self, ctx):
        try:
            arguments = ctx.message.content.split(self.command + ' ')[1]
            if arguments.lower() == 'latest':
                await self.post_version(ctx.channel, arguments)
            else:
                await self.post_version(ctx.channel, arguments)
        except Exception as e:
            print(e)
            await self.post_version(ctx.channel)
    async def post_version(self, channel, version=None):
        link = await self.generate_link(version)
        req = requests.get(link)
        if req.status_code == 404:
            return await channel.send("Invalid version.")
        tree = html.fromstring(req.content)
        image_link = 'https://minecraft.gamepedia.com' + tree.xpath('//div[@class="infobox-imagearea animated-container"]/div/a/@href')[0]
        image = html.fromstring(requests.get(image_link).content).xpath('//div[@class="fullImageLink"]/a/@href')[0]
        title = link.split('https://minecraft.gamepedia.com/')[1].replace('_', ' ')
        features_map = {}
        path = '//div[@class="mw-parser-output"]/'
        i = 1
        while len(str(features_map)) + len(desc) < 512:
            key = tree.xpath(path + 'dl[{0}]/dt/descendant-or-self::*/text()'.format(i))[0]
            value = ['• ' + ''.join(i.xpath('descendant-or-self::*/text()')) for i in tree.xpath(path + 'ul[{}]/li'.format(i))]
            features_map[key] = value
            i += 1
        while len(str(features_map)) + len(desc) > 1536:
            del features_map[features_map.keys()[-1]][-1]
        if '-pre' in title:
            title = title.replace('-pre', ' Pre-release ')
        embed = discord.Embed(description="**[{0}]({1})".format(title, link))
        embed.set_image(url=image)
        for key, value in features_map.items():
            if not key:
                key = '⠀'
            if not value:
                value = '⠀'
            embed.add_field(name=key, value='\n'.join(value), inline=False)
        await channel.send(embed=embed)
    async def generate_link(self, version=None):
        if version:
            link = 'https://minecraft.gamepedia.com/Java_Edition_' + version.lower()
        else:
            request = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
            latest = request.json()['versions'][0]
            link = 'https://minecraft.gamepedia.com/Java_Edition_' + latest['id']
        return link
class Number_To_RoNum(commands.Cog):    command = prefix + 'ronum'
    def help_message(self):
        return """Converts a number to a roman numeral.
``{} (number)``
 \> Returns the Roman Numeral equivalent of a whole number.   (Note: Try not to input numbers larger than 9999.)""".format(self.command)
    @commands.command()
    @not_self()
    async def ronum(self, ctx):
        message = ctx.message        args = ''.join(message.content.split()[1:])        if not args:            return await module_help(message.channel, self.__class__.__name__)
        try:            await message.channel.send(int2ronum(int(args)))        except discord.errors.HTTPException:            await message.channel.send("Output is too long for Discord.")        except ValueError:            await message.channel.send("Input must be a whole number.")class Thread(commands.Cog):    command = prefix + 'thread'    def help_message(self):        return """W.I.P
``{0} create (threadName)`` \> WIP``{0} (threadName) (message)`` \> WIP""".format(self.command)    @commands.command()    @not_self()    async def thread(self, ctx):        message = ctx.message        embed = discord.Embed()
        embed.add_field(name = message.author.name, value = message.content, inline = False)
        await message.channel.send(embed = embed)
class Random(commands.Cog):
    command = prefix + 'random'
    def keywordFunc(self, value):
        prefix = ['Dumb', 'Random', 'Annoying', 'Round', 'Tiny', 'Gay', 'Inconsequential', 'Uncalled For', 'Pedantic', 'Based']
        color  = ['Blue', 'Black', 'White', 'Green', 'Red', 'Yellow', 'Purple', 'Cyan', 'Navy', 'Brown']
        object = ['Ball', 'Book', 'Bimbo', 'Bird', 'Bitch', 'Baby', 'Rat', 'Sword', 'Scythe', 'Bow', 'E-Girl', 'Blanket', 'Bottle', 'Cake', 'Door', 'Table', 'Glass', 'Window', 'Bread', 'Bee', 'Dog', 'Horse', 'Rock', 'Crystal', 'Gun', 'Chewing Gum', 'Cigarette', 'Cigar', 'CD', 'Phone', 'Axe', 'Stick', 'Car', 'Worm', 'Cloth', 'Toy', 'Bat', 'Snake', 'Cat', 'Closet', 'Mirror', 'MILF', 'DILF', 'Soup', 'Popcorn', 'Bowl', 'Flag', 'Carpet', 'Dress', 'Hair', 'Camera', 'Chair', 'TV', 'Toilet', 'Chimney', 'Furnace', 'Chest', 'Pickaxe', 'Hoe', 'Crossbow', 'Cape', 'Apple', 'Pie', 'Wire', 'Wine', 'Gasoline', 'Champagne', 'Lasagna', 'Spaghetti', 'Skeleton', 'Zombie', 'Vampire', 'Buffalo', 'Angel', 'Demon', 'The Holy Bable', 'Fingernail', 'Toenail', 'Button', 'Knife', 'Dagger', 'Lighter', 'Lightbulb', 'Pepper Spray', 'Koala', 'Tiger', 'Lion', 'Leaf', 'Alpaca', 'Zebra', 'Dolphin', 'Plankton', 'Weed', 'Flower', 'Clock', 'Tooth', 'Teeth', 'Sheep', 'Wolf', 'Fox', 'Ocelot', 'Turtle', 'Tower', 'Train', 'Sun', 'Moon', 'Star', 'Crab', 'Pen', 'Paper', 'Scissors', 'Pineapple', 'Egg', 'Salad', 'Whip', 'Noose', 'Crown', 'Glasses', 'Pony', 'Mask', 'Tissue', 'Sunglasses', 'Drill', 'Hammer', 'Bucket', 'Bag', 'Can', 'Toaster', 'Fridge', 'Ashtray', 'Helmet', 'Towel', 'Armor', 'Shoe', 'Shoes', 'Ant', 'Spider', 'Ladybug', 'Chicken', 'Squid', 'Snail', 'Butterfly', 'Kangaroo']
        suffix = ['of The Damned', 'of Epicness', 'of Randomness', 'of Complete Madness', 'of the Cringe', '', 'of the Rat King']
        return eval(value)    keywordList = list(keywordFunc.__code__.co_varnames)
    del keywordList[0]    del keywordList[0]
    def help_message(self):
        help_message = """Returns a message with any keywords replaced with random words.
``{0} (arguments)``
 \> Returns a string with any keywords in (arguments) replaced.
   Keywords: """.format(self.command)
        for keyword in self.keywordList:
            help_message = help_message + '[{}] '.format(keyword)
        return help_message
    @commands.command()    @not_self()
    async def random(self, ctx):
        message = ctx.message
        try:
            this_message = message.content.split('{} '.format(self.command), 1)[1]
            if this_message == '':
                raise
        except:
            await message.channel.send('Invalid Arguments. Type __{}help Random__ for more information.'.format(prefix))
            return
        for i in range(this_message.count('[')):
            for key in self.keywordList:
                if '[{}]'.format(key) in this_message:                    getList = self.keywordFunc(key)
                    this_message = this_message.replace('[{}]'.format(key), random.choice(getList), 1) + ' '
                    break
        await message.channel.send(this_message)
class Insult_Generator(commands.Cog):    command = prefix + 'insult'    def help_message(self):        return """Generate random insults.``{0}`` \> Returns a procedurally generated insult.``{0} s`` \> Returns a procedurally generated PG-13 insult.""".format(self.command)    @commands.command()    @not_self()    async def insult(self, ctx):        message = ctx.message        try:            argument = message.content.split()[1]            if argument == 's':                insult = generate_insult(True)        except IndexError:            insult = generate_insult()        await message.channel.send(insult)
class Skin(commands.Cog):
    command = prefix + 'skin'
    def help_message(self):
        return """Send a player's Minecraft skin.``{0} (player) [upscale]``
 \> Returns a Minecraft (player)'s skin.
   Optionally, specify a [whole number] to upscale the image by.""".format(self.command)
    @commands.command()    @not_self()
    async def skin(self, ctx):
        message = ctx.message
        try:
            arguments = message.content.split()
            del arguments[0]
            argument = arguments[0]
            if argument == '':
                raise
        except:
            return await module_help(message.channel, self.__class__.__name__)
        try:
            upscale = int(arguments[1])
            if upscale < 1:
                raise ValueError
            if upscale > 10:
                raise ValueError
        except IndexError:
            upscale = 1
        except ValueError:
            return await message.channel.send("Upscale value can only be a whole number from 1 to 10.")
        try:
            content = get_JSON('https://api.mojang.com/users/profiles/minecraft/' + argument)
        except EmptyLinkError:
            return await message.channel.send("Unknown Player.")
        except JSONDecodeError:
            return await message.channel.send("Something went wrong, try again.")
        skinName = content['name']
        try:
            content = get_JSON('https://sessionserver.mojang.com/session/minecraft/profile/' + content['id'])
        except JSONDecodeError:
            return await message.channel.send("Something went wrong, try again.")
        code = content['properties'][0]['value']
        decodeMe = code.encode('ascii')
        decoded = base64.b64decode(decodeMe).decode('ascii')
        content = json.loads(decoded)
        try:
            skinURL = content['textures']['SKIN']['url']
        except FailedResponseError:
            return await message.channel.send("Something went wrong, try again.")        except:
            return await message.channel.send("{} does not have a skin.".format(skinName))
        skinFile = await url_to_file(skinURL)        if upscale > 1:
            skinImage = Image.open(skinFile)
            skinImage = skinImage.resize((skinImage.size[0] * upscale, skinImage.size[1] * upscale), Image.NEAREST)            skinFile = io.BytesIO()
            skinImage.save(skinFile, 'png')            skinFile.seek(0)
        await message.channel.send("{}\'s Skin:".format(skinName), file=discord.File(skinFile, filename='{}.png'.format(skinName)))

class Suggestions(commands.Cog):
    suggestions_channel = 807271131924660264
    suggestion_discussion_channel = 630500899654991888
    async def __asinit__(self):
        try:
            self.sug_disc_chnl = await bot.fetch_channel(self.suggestion_discussion_channel)
        except Exception as e:
            print(e)
    def help_message(self):
        return "Tracks suggestions posted in <#{0}> and posts them in <#{1}>".format(self.suggestions_channel, self.suggestion_discussion_channel)
    @commands.Cog.listener()
    @not_self()
    async def on_message(self, message):
        if message.channel.id == self.suggestions_channel:
            if str(message.type) == 'MessageType.pins_add':
                return
            await react_to_message(message, ['✅', ':white_x_mark:737044020165083289'])
            await embed_message(self.sug_disc_chnl, message)

class Roll(commands.Cog):
    command = '/roll'
    def help_message(self):
        return """Roll a questionably large die.
``{0} (number)``
 \> Returns a number between 1 and the (specified number).
``{0} (amount) [number]``
 \> Returns an [amount of numbers] between 1 and the (specified number).
""".format(self.command)

class MOTD(commands.Cog):
    command = '/motd'
    def help_message(self):
        return """W.I.P.
``{0} (message)``
 \> Changes Sorrowfall's Message Of The Day to the specified (message).""".format(self.command)

class Ping(commands.Cog):
    command = '/ping'
    def help_message(self):
        return """W.I.P.
``{0}``
 \> Pong!""".format(self.command)

class Random_Message(commands.Cog):
    command = prefix + 'randmessage'
    def help_message(self):
        return """Sends a random message from a channel.``{0} (channel)``
 \> Sends an embed displaing a random message from the specified (channel).""".format(self.command)
    @commands.command()    @not_self()
    async def randmessage(self, ctx):
        message = ctx.message
        try:
            arguments = message.content.split(self.command + ' ')[1]
        except:
            await module_help(message.channel, self.__class__.__name__)
            return
        try:
            thisChannel = arguments.split('<#')[1].split('>')[0]
            thisChannel = await bot.fetch_channel(int(thisChannel))
        except:
            await message.channel.send("Could not find that Channel.")
            return
        if thisChannel.is_nsfw() and not message.channel.is_nsfw():
            await message.channel.send("You can only get messages from NSFW Channels inside of NSFW Channels.")
            return
        randomMessage = await random_message(thisChannel)        await embed_message(message.channel, randomMessage)

class Online(commands.Cog):
    command = '/online'
    def help_message(self):
        return """W.I.P.
``{0}``
 \> Returns a list of all members connected to Sorrowfall.""".format(self.command)

class Avatar(commands.Cog):
    command = prefix + 'avatar'
    def help_message(self):
        return """Get someone's profile picture.
``{0} (name)``
 \> Returns a Server Member's avatar.""".format(self.command)
    @commands.command()    @not_self()
    async def avatar(self, ctx):
        message = ctx.message
        try:
            arguments = message.content.split(self.command + ' ')[1]
            thisMember = message.guild.get_member_named(arguments)
            if thisMember == None:
                return await message.channel.send("Could not find the Member.")
            await self.postAvatar(message, thisMember)
        except:            await self.postAvatar(message, message.author)    async def postAvatar(self, message, target):        if target.is_avatar_animated():
            frmt = 'gif'
        else:
            frmt = 'png'        try:
            file = await url_to_file(target.avatar_url_as(format=frmt))        except FailedResponseError:            return await message.channel.send("Failed to download the image, try again.")        if message.author == target:
            await message.channel.send("Your Avatar Is:", file=discord.File(file, target.name + '.{}'.format(frmt)))        else:            await message.channel.send("{}'s Avatar Is:".format(target.display_name), file=discord.File(file, target.name + '.{}'.format(frmt)))
class ToDo(commands.Cog):
    command = prefix + 'todo'
    def help_message(self):
        return """Keep tracks of things that you need to do.
``{0} add (task)``
 \> Adds a task to your To-Do list.
``{0} list [member_name]``
 \> Shows your [or someone else's] To-Do list.
``{0} remove (index)``
 \> Removes a task at the index from your To-Do list.""".format(self.command)
    @commands.command()    @not_self()
    async def todo(self, ctx):        message = ctx.message
        arguments = message.content.split()
        del arguments[0]
        if arguments == []:
            return await module_help(ctx.channel, self.__class__.__name__)        if not os.path.exists('todo.json'):            with open('todo.json', 'w+', encoding='utf-8') as i:                pass        with open('todo.json', 'r+', encoding='utf-8') as todoFile:            try:                todoMessage = json.loads(todoFile.read())            except:                todoMessage = dict()
        if arguments[0].lower() == 'add':
            try:
                argument = message.content.split('add', 1)[1]                if argument.startswith(' '):                    argument = argument.split(' ', 1)[1]                if argument.startswith('\n'):                    argument = argument.replace('\n', '', 1)
            except:
                await message.channel.send('Task can not be empty.')
                return            for space in range(argument.count('\n\n')):                try:                    argument = argument.replace('\n\n', '\n')                except:                    pass            try:                todoMessage[str(message.author.id)].append(argument)            except:                todoMessage[str(message.author.id)] = [argument]
            await message.channel.send('Added to your To-Do list:```ini\n{}```'.format(argument))
            with open('todo.json', 'w+', encoding='utf-8') as file:
                json.dump(todoMessage, file, indent=2)
        elif arguments[0].lower() == 'list':
            try:
                argument = message.content.split('list ', 1)[1].replace('\n', '')                member = message.guild.get_member_named(argument)
                if member == None:
                    await message.channel.send('Could not find that Member.')
                    return
            except:
                member = message.author
            try:
                todoList = todoMessage[str(member.id)]                if todoList == []:
                    raise KeyError            except KeyError:                todoMessage[str(member.id)] = []                await message.channel.send('This To-Do list is empty.')
                return
            tasks = member.display_name + "'s To-Do List:```ini\n"
            for index, task in enumerate(todoList, start=1):
                spaces = ' ' * (len(str(index)) + 3)
                tasks = tasks + '[{}] '.format(str(index)) + task.replace('\n','\n' + spaces) + '\n'            tasks = tasks + '```'
            await message.channel.send(tasks)
        elif arguments[0].lower() == 'remove':
            try:
                index = int(message.content.split('remove ', message.content.index('remove '))[1].replace('\n', ' '))
                if index > 0:
                    index = index - 1
            except:
                await message.channel.send("Index can not be empty.")
                return
            try:
                todoList = todoMessage[str(message.author.id)]                if todoList == []:
                    raise            except KeyError:
                todoMessage[str(message.author.id)] = []
                raise
            except IndexError:
                await message.channel.send("Your To-Do list is empty.")
                return
            try:
                e = todoList[index]
            except:
                await message.channel.send("Invalid Index.")
                return
            poppedValue = todoList.pop(index)
            todoMessage[str(message.author.id)] = todoList
            with open('todo.json', 'w+', encoding='utf-8') as file:
                json.dump(todoMessage, file, indent=2)
            await message.channel.send("Removed from your To-Do list:```ini\n{}```".format(poppedValue))
        else:
            await module_help(message.channel, 'ToDo')

class Say(commands.Cog):
    command = prefix + 'say'
    def help_message(self):
        return '''Send a message as the bot.
``{0} (arguments)``
 \> Sends a message containing any (arguments) sent.
'''.format(self.command)
    @commands.command()    @not_self()
    async def say(self, ctx):
        try:
            await ctx.channel.send(ctx.message.content.split(self.command + ' ', 1)[1])
        except:
            return

class Poll(commands.Cog):
    command = ['(S)', 'Poll;']
    def help_message(self):
        return 'Reacts with [✅] and [X] emotes on messages starting with "{0[0]}" or "{0[1]}"...'.format(self.command)
    @commands.Cog.listener()    @not_self()
    async def on_message(self, message):
        for command in self.command:
            if message.content.lower().startswith(command.lower()):
                await react_to_message(message, ['✅', ':white_x_mark:737044020165083289'])
                if 'suggestions' in message.channel.name:
                    await message.pin()

class Yes_Poll(commands.Cog):    command = ['{S}', 'Poll..']
    def help_message(self):
        return 'Reacts with 2 (two) [✅] emotes on messages starting with "{0[0]}" or "{0[1]}".'.format(self.command)
    @commands.Cog.listener()    @not_self()
    async def on_message(self, message):
        for command in self.command:
            if message.content.lower().startswith(command.lower()):
                await react_to_message(message, ['✅', ':whiter_checker_marker:752987624188280972'])
class Embed_Links(commands.Cog):
    def help_message(self):
        return """Sends an embed displaying the content of linked messages.
Turn on developer mode to copy message links."""
    @commands.Cog.listener()    @not_self()
    async def on_message(self, message):
        if 'https://' in message.content.lower() and 'discord' in message.content.lower():
            for word in message.content.lower().split():
                if 'https://' not in word:
                    continue
                try:
                    if 'discord' in word.split('https://', 1)[1].split('.com/channels/', 1)[0]:
                        linked_message = await link_to_message(word)
                        await embed_message(message.channel, linked_message)
                except:
                    pass

class Greeting(commands.Cog):
    def help_message(self):
        return 'Replies whenever someone greets SorrowBot.'
    @commands.Cog.listener()    @not_self()
    async def on_message(self, message):
        if 'sorrowbot' in message.content.lower():
            greetings = ['hello ', 'sup ', 'hi', 'yo ', 'hey']
            for greet in greetings:
                if '{} sorrowbot'.format(greet) in message.content.lower():
                    await message.channel.send(random.choice(greetings).title().replace(' ', '') + ' ' + message.author.name + '!')

class Help(commands.Cog):
    command = prefix + 'help'
    def __init__(self, bot):
        self.modules = split_every(module_list, 6)
        self.module_pages = len(modules)

    def help_message(self):
        return """Provides help messages for all active modules.\n
``{0} (number)``
 \> View more modules.
``{0} (module)``
 \> Provides help for currently running modules.
""".format(self.command)

    @commands.command()
    @not_self()
    async def help(self, ctx):
        message = ctx.message
        channel = message.channel
        try:
            arguments = message.content.lower().split(self.command + ' ')[1].replace(' ', '_')
            if arguments.isdigit():
                return await self.help_menu(channel, int(arguments))
            else:
                return await self.help_module(channel, arguments)
        except IndexError:
            await self.help_menu(channel, 1)

    async def help_menu(self, channel, number):
        if number > 0:
            number -= 1
        if number >= self.module_pages:
            return await channel.send("The number you have entered ({0}) is too big, it must be at most {1}".format(number + 1, self.module_pages))
        embed = discord.Embed(description="**Modules List - Page {0} out of {1}**\n⠀".format(number + 1, self.module_pages))
        for module in self.modules[number]:
            desc = module_map[module]
            if '\n' in desc:
                desc = desc.split('\n', 1)[0]
            if not desc:
                desc = "This module doesn't have a help message."
            embed.add_field(name=module.replace('_', ' ') + " Module", value=desc, inline=True)
        embed.set_footer(text="⠀\nType {0} (module) for more information on a Module\nType {0} (page) to see more Modules".format(self.command))
        await channel.send(embed=embed)

    async def help_module(self, channel, module):
        if module.endswith('_module'):
            module = module.rsplit('_module', 1)[0]
        for val in module_list:
            if val.lower() == module:
                return await module_help(channel, val)

# Modules End #

@bot.listen('on_ready')
async def on_ready():
    await async_init()
    activity = discord.Game(name='Usage: {}help'.format(prefix))
    await bot.change_presence(activity=activity)
    print_servers()

async def async_init():
    for module in modules:
        try:
            await module.__asinit__(module)
        except AttributeError:
            pass
def load_modules():
    global modules, module_list, module_map
    modules = []
    module_list = []
    module_map = {}
    glb = list(globals().items())
    for key, value in list(globals().items()):
        try:
            if callable(value.help_message):
                bot.add_cog(eval(key + '(bot)'))
                modules.append(value)
                module_list.append(key)
                try:
                    desc = value.help_message(value)
                except Exception as e:
                    print(e)
                    desc = None
                module_map[key] = desc
        except AttributeError:
            pass
    print("Loaded Modules: [{}] ".format(len(module_list)) + ', '.join([module.replace('_', ' ') for module in module_list]) + '.\n')

def start_bot():
    try:
        bot.run(os.environ.get('SORROWBOT_TOKEN'))
    except:
        input("Invalid bot token.")
def print_servers():    server_list = [server.name for server in bot.guilds]    print("Connected Servers: [{}] ".format(str(len(server_list))) + ', '.join(server_list) + '\n')

if __name__ == '__main__':    load_modules()
    start_bot()