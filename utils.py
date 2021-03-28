#from start import bot
from random import choice
from discord.ext import commands
from discord import Embed
from debug_utils import print_exception
from start import bot
from aiohttp import ClientSession
from io import BytesIO
from json import loads
from datetime import datetime, timedelta
import random
from time import time

def timer(f):
    def w(*a):
        o = time()
        f(*a)
        print(o - time())
    return w

async def get_JSON(url):
    async with ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

async def random_message(channel):
    creation_date = channel.created_at
    new_date = random_date(datetime.now(), creation_date)
    channel_history = channel.history(limit=32, oldest_first=True, after=new_date)
    message_list = await channel_history.flatten()
    if not message_list:
        channel_history = channel.history(limit=32, oldest_first=True, before=new_date)
        message_list = await channel_history.flatten()
    if not message_list:
        return None
    this_message = message_list[random.randint(0, len(message_list)-1)]
    return this_message

def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randint(int_delta, 0)
    return start + timedelta(seconds=random_second)

async def error_message(ctx, message):
    return await ctx.send(embed=Embed(description=str(message), color=0xDC2D43))

class InvalidEmbedDict(Exception):
    pass

def get_embed_from_json(json):
    try:
        json_dict = loads(json)
    except TypeError:
        json_dict = json
    # last-second changes
    json_dict = {index.lower() : value for index, value in json_dict.items()}
    if 'color' in json_dict:
        if isinstance(json_dict['color'], str):
            if json_dict['color'].startswith('#'):
                json_dict['color'] = json_dict['color'].split('#', 1)[1]
            json_dict['color'] = int('0x' + json_dict['color'], 0)
    if 'embed' in json_dict:
        json_dict = json_dict['embed']
    if 'description' in json_dict:
        if isinstance(json_dict['description'], list):
            json_dict['description'] = '\n'.join(json_dict['description'])
    if 'timestamp' in json_dict:
        json_dict['timestamp'] = json_dict['timestamp'].replace('Z', '000+00:00')
    field_list = []
    if 'fields' in json_dict:
        for field in json_dict['fields']:
            try:
                if not field['name']:
                    field['name'] = '\u200b'
            except KeyError:
                field['name'] = '\u200b'
            try:
                if not field['value']:
                    field['value'] = '\u200b'
            except KeyError:
                field['value'] = '\u200b'
            field_list.append(field)
        json_dict['fields'] = field_list
    # convert to embed
    embed = Embed.from_dict(json_dict)
    if not embed.to_dict():
        raise InvalidEmbedDict
    return embed

async def url_to_file(url):
    async with ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            return BytesIO(await resp.read())

async def url_status(url):
    async with ClientSession() as session:
        async with session.get(url) as resp:
            return resp.status

async def embed_message(channel, message):
    embed_message = message.content
    if message.content == None:
        raise EmptyMessage("Message is embeded or is a system \\\\\message")
    #if message.embeds != []:
    #    return await message.channel.send("Cannot send Embeded messages (yet).")
    if str(message.type) == 'MessageType.pins_add':
        embed_message = "{} pinned a message to this channel. See all the pins.".format(message.author.display_name)
    elif str(message.type) == 'MessageType.new_member':
        embed_message = "{} Joined the server.".format(message.author.display_name)
    this_embed = Embed(description=embed_message + '\n\n[(jump)]({})'.format(message.jump_url), timestamp=message.created_at)
    this_embed.set_author(url='https://discord.com/users/{}'.format(message.author.id), name=message.author.name, icon_url=message.author.avatar_url)
    this_embed.set_footer(text='#' + message.channel.name)
    this_attachment = (message.attachments[0:]+[None])[0]
    if this_attachment != None:
        if this_attachment.filename.endswith(('.png', '.gif', '.jpeg', '.jpg')):
            this_embed.set_image(url=this_attachment.url)
        else:
            this_embed.description = message.content + f'\n[<{this_attachment.filename}>]({this_attachment.url})\n\n[(jump)]({message.jump_url})'
    await channel.send(embed=this_embed)

async def module_help(channel, module):
    from start import bot
    try:
        try:
            desc = module.help_message()
        except AttributeError:
            desc = "This module doesn't have a help message."
        embed = Embed(description="**{} Module**".format(module.__class__.__name__.replace('_', ' ')))
        embed.add_field(name='\u200b', value=desc, inline=False)
        await channel.send(embed=embed)
    except Exception as e:
        print(e)

def not_self():
    def predicate(ctx):
        return ctx.author != bot.user
    return commands.check(predicate)

def split_every(obj, count):
    return [obj[i * count:(i + 1) * count] for i in range((len(obj) + count - 1) // count )]

num_ronum_dict = {
    900: 'CM', 500: 'D', 400: 'CD', 100: 'C', 90: 'XC',
      50: 'L',  40: 'XL',  10: 'X',   9: 'IX',   5: 'V',  4: 'IV', 1: 'I'
    }

num_supertext_dict = {
    '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉', '0': '₀'
}

def num_to_superscript(input_number):
    result = str(input_number)
    for number, superscript in num_supertext_dict.items():
        result = result.replace(number, superscript)
    return result

def int_to_full_ronum(input_number):
    if not input_number:
        return 'N'
    result = ''
    thousand = int(input_number / 1000)
    if thousand:
        result = 'M' * thousand
        input_number -= 1000 * thousand
    for number, ronum in num_ronum_dict.items():
        while input_number >= number:
            result = result + ronum
            input_number -= number
    return result

def int_to_ronum(input_number):
    if not input_number:
        return 'N'
    result = ''
    thousand = int(input_number / 1000)
    if thousand:
        if thousand > 1:
            result = 'M' + num_to_superscript(thousand)
        else:
            result = 'M'
        input_number -= 1000 * thousand
    for number, ronum in num_ronum_dict.items():
        while input_number >= number:
            result = result + ronum
            input_number -= number
    return result

def ronum_to_int(input_string):
    input_string = input_string.upper()
    if input_string == 'N':
        return 0
    result = 0
    thousand = input_string.count('M')
    if thousand:
        result = 1000 * thousand
        input_string = input_string.rsplit('M', 1)[1]
    for number, ronum in num_ronum_dict.items():
        while input_string.startswith(ronum):
            result += number
            input_string = input_string.split(ronum, 1)[1]
    return result

def generate_insult(safe=False):
    main = ['well played (noun)', 'you are (adjct) (noun)', 'you are (adjct) (noun)', 'eat a (noun) (noun)',
    'eat a (noun)', '(verb)', 'i will (verb) you', 'who is this (adjct) (noun)']
    insults = {
    "noun": ['nerd', 'weakling', 'dork', 'donkey', 'maggot', 'cretin', 'jerk', 'idiot', 'fool', 'butt', 'nerd', 'freak', 'buffoon', 'tool',
    'dunce', 'blockhead', 'pinhead', 'chump', 'donkey', 'muppet'],
    "verb": ['kiss', 'kick', 'punch'],
    "adjct": ['french', 'stupid', 'weak', 'dumb', 'fat', 'ugly', 'thick', 'daft', 'long', 'tiny', 'bumbling', 'absolute']
    }
    if not safe:
        main += ['i will (verb) your mother', '(verb) yourself', '(verb) you', 'i (verb) in your room', 'choke on a (noun) and (verb)']
        newInsults = {
        "noun": ['retard', 'fuck', 'shit', 'ass', 'imbecile', 'ass', 'asshole', 'turd', 'sucker', 'piss', 'bitch', 'tard', 'fuckhead'],
        "verb": ['fuck', 'shit', 'kill', 'shit', 'hang', 'pass'],
        "adjct": ['retarded', 'motherfucking']
        }
        for key, values in newInsults.items():
            for value in values:
                insults[key].append(value)
    insult = choice(main)
    for key, key_insults in insults.items():
        key = '(' + key + ')'
        while key in insult:
            insult = insult.replace(key, choice(key_insults), 1)
    remove_characters = choice(range(-2, 3))
    while remove_characters > 0:
        insult = insult.replace(insult[choice(range(len(insult)))], '', 1)
        remove_characters -= 1
    return insult