from os.path import isfile
import nextcord
from nextcord.ext import commands
import nextcord.utils
from nextcord.ext.commands import BadArgument
import asyncio
import random
import traceback
from difflib import get_close_matches
import os
import requests
import json
import aiohttp
import io
import wikipediaapi
import wikipedia
import unidecode
from datetime import datetime, timedelta
import typing
import fortune
import time
import ffmpeg
import yt_dlp
import typing
import logging
import transliterate
import markov
import json
import g4f
from os import getenv
from dotenv import load_dotenv
from categories import buildHelpEmbed, buildCategoryEmbeds, helpCategory
from balaboba import Balaboba
from config import *
from agify import AsyncNameAPI
import httpx
import demapi
from nextcord import Interaction

print(g4f.Provider.Ails.params)

genaiDataPath = 'data/genai_info.json'
imagesDataPath = 'data/image_urls.json'

bb = Balaboba()

word_dict = []

if isfile(genaiDataPath):
    with open(genaiDataPath) as f:
        genData = json.load(f)
else:
    genData = {}

if isfile(imagesDataPath):
    with open(imagesDataPath) as f:
        imgData = json.load(f)
else:
    imgData = {}

genAiArray: dict[str, markov.MarkovGen] = {k: markov.MarkovGen(states=v['state'], config=v['config']) for k,v in genData.items()}
image_list: dict[str, list[str]] = imgData
msgCounter = 0

print("AdventurerUp Corporation")
kgb = commands.Bot(command_prefix=prefix, strip_after_prefix=True, intents=nextcord.Intents.all())
kgb.persistent_views_added = False
kgb.remove_command("help")
load_dotenv()

GUILD_SEEK_FILENAME = "data/guild_seek.json"

HELP_EMB: typing.Union[nextcord.Embed, None] = None
HELP_CAT_EMB: typing.Union[list[nextcord.Embed], None] = None
HELP_CAT_HIDDEN: typing.Union[dict[str, nextcord.Embed], None] = None

if not os.path.isfile('data/guild_seek.json'):
    with open('data/guild_seek.json', 'w', encoding='utf-8') as f:
        f.write('{}')

logger = logging.getLogger('nextcord')
logger.setLevel(logging.ERROR)

class nextcordHandler(logging.Handler):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        super().__init__()

    async def send_log_message(self, message):
        channel = kgb.get_channel(self.channel_id)
        await channel.send(message)

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.ensure_future(self.send_log_message(log_entry))

async def change_status():
    statuses = "kgb!help", "версия 3.0", "на {} серверах!"
    index = 0
    while not kgb.is_closed():
        servers_count = len(kgb.guilds)
        status = statuses[index].format(servers_count)
        await kgb.change_presence(activity=nextcord.Game(name=status))
        index = (index+1) % len(statuses)
        await asyncio.sleep(10)

def format_overwrites(overwrites):
    formatted = []
    for item in overwrites.items():
        perms = item[1]
        perms_list = []
        for perm, value in perms:
            perms_list.append(f"{perm}: {value}")
        perms_str = ", ".join(perms_list)
        formatted.append(f"{item[0].name}: {perms_str}")
    return "\n".join(formatted)

def get_guild_names():
    return [guild.name for guild in kgb.guilds]

def get_guild_info(guild):
    users = [{"name": str(user), "tag": str(user.discriminator)} for user in guild.members if not user.bot]
    return {"name": guild.name, "users": users}

def get_all_guild_info():
    return [get_guild_info(guild) for guild in kgb.guilds]

async def update_guild_seek():
    guild_seek = {}
    for guild in kgb.guilds:
        guild_info = {
            "name": guild.name,
            "users": []
        }
        for member in guild.members:
            user_info = {
                "name": member.name,
                "discriminator": member.discriminator
            }
            guild_info["users"].append(user_info)
        guild_seek[str(guild.id)] = guild_info
    with open(GUILD_SEEK_FILENAME, "w", encoding="utf-8") as f:
        json.dump(guild_seek, f, ensure_ascii=False, indent=4)

async def search_user(user_name):
    for guild_info in get_all_guild_info():
        guild_name = guild_info['name']
        for user in guild_info['users']:
            if user_name.lower() in user['name'].lower():
                return f"{user['name']}#{user['tag']} is in {guild_name}"
    return f"{user_name} not found"
      
def get_guild_names():
    return sorted([guild.name for guild in kgb.guilds])
async def update_guild_names():
    guild_names = get_guild_names()
    with open("data/guild_names.json", "w", encoding='utf-8') as f:
        json.dump(guild_names, f, ensure_ascii=False, indent=4)
      
def no_format(user):
    if isinstance(user, nextcord.Member):
        return f"{user.name}#{user.discriminator}"
    return user.name
try:
    with open("data/channels.json", "r") as f:
        channels = json.load(f)
except FileNotFoundError:
    channels = {}
  
if not os.path.exists('data/warn.json'):
    with open('data/warn.json', 'w') as f:json.dump({}, f)
      
with open('data/warn.json', 'r') as f:warnings = json.load(f)
  
if not os.path.exists('data/stanwarns.json'):
    with open('data/stanwarns.json', 'w') as f:f.write('{}')

@kgb.event
async def on_ready():
    handler = nextcordHandler(channel_id=1123467774098935828)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    logger.info('Бот в полной боевой готовности!')
    kgb.loop.create_task(change_status())
    await update_guild_names()
    while True:
        try:
            await asyncio.wait_for(update_guild_names(), timeout=30.0)
        except asyncio.TimeoutОшибка:
            print("update_guild_names() timed out")
        await update_guild_seek()
        await asyncio.sleep(3600)
      
      
@kgb.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    if guild_id in channels:
        channel_id = channels[guild_id]
        channel = kgb.get_channel(int(channel_id))
        if channel:
          await channel.send(f"Приветствую вас на этом сервере, {member.mention}!")

@kgb.event
async def on_message(message):
    if message.channel.id == 1067091686725001306:
        with open('data/retr.txt', 'r') as file:
            channel_ids = file.readlines()
            channel_ids = [id.strip() for id in channel_ids]

        for channel_id in channel_ids:
            channel = kgb.get_channel(int(channel_id))
            if channel:
                embed_color = random.choice(['FF0000', 'FFFF00'])
                embed = nextcord.Embed(
                    title=f'Сообщение из канала #{message.channel.name}:',
                    description=message.content,
                    color=nextcord.Color(int(embed_color, 16))
                )
                if len(message.attachments) > 0:
                    for attachment in message.attachments:
                        embed.set_image(url=attachment.url)
                await channel.send(embed=embed)

    replied = False

    if message.author != kgb.user:
        channelId = str(message.channel.id)
        if channelId in genAiArray and genAiArray[channelId].config['read']:
            genAi = genAiArray[channelId]
            genAi.addMessage(message.content)
            if genAi.config['reply_on_mention']:
                for user in message.mentions:
                    if user.id == kgb.user.id:
                        await message.reply(genAi.generate()[:2000])
                        replied = True
                        break
            
            if channelId not in image_list: image_list[channelId] = []

            if message.attachments: image_list[channelId].extend([str(v) for v in message.attachments])

        global msgCounter
        msgCounter = msgCounter + 1

        if msgCounter % 10 == 0:
            with open(genaiDataPath, 'w') as f:
                json.dump({k: {
                    'state': v.dumpState(),
                    'config': v.config,
                } for k,v in genAiArray.items()}, f)

            with open(imagesDataPath, 'w') as f:
                json.dump(image_list, f)

    if message.content == "<@1061907927880974406>" and not replied:
        return await message.channel.send("Мой префикс - `kgb!`")

    await kgb.process_commands(message)

@kgb.event
async def on_member_remove(member):
    guild_id = str(member.guild.id)
    if guild_id in channels:
        channel_id = channels[guild_id]
        channel = kgb.get_channel(int(channel_id))
        if channel:
            await channel.send(f"Прощай, {member.mention}!")
          
@kgb.event
async def on_command_error(ctx, exc):
  if isinstance(exc, BadArgument):
    await ctx.reply(embed = nextcord.Embed(
      title = "Ошибка:",
      description = "Найдены некорректные аргументы",
      color = nextcord.Colour(0xFF0000)
    ))
  elif isinstance(exc, commands.CommandNotFound):
    cmd = ctx.invoked_with
    cmds = [cmd.name for cmd in kgb.commands]
    matches = get_close_matches(cmd, cmds)
    if len(matches) > 0:
      await ctx.reply(embed = nextcord.Embed(
        title = "Ошибка:",
        description = f"Команда `kgb!{cmd}` не найдена, может вы имели ввиду `kgb!{matches[0]}`?",
        color = nextcord.Colour(0xFF0000)
      ))
    else:
      return await ctx.reply(embed = nextcord.Embed(
        title = "Ошибка:",
        description = "Команда не найдена. \nПожалуйста, напишите `kgb!help` чтобы посмотреть полный список команд!", 
        color = nextcord.Colour(0xFF0000)
      ))
  elif isinstance(exc, commands.CommandOnCooldown):
    await ctx.reply(embed = nextcord.Embed(
      title = "Эта команда перезагружаеться!",
      description = f"Повторите попытку через {round(exc.retry_after, 2)} секунд.",
      color = nextcord.Colour(0xFF0000)
    ))
  elif isinstance(exc, commands.MissingPermissions):
    await ctx.reply(embed = nextcord.Embed(
      title = "Ошибка:", 
      description = "Вы не имеете прав администратора!", 
      color = nextcord.Colour(0xFF0000)
    ))
  elif isinstance(exc, commands.MissingRequiredArgument):
    await ctx.reply(embed = nextcord.Embed(
      title = "Ошибка:",
      description = f"Пропущен аргумент: `{exc.param.name}`!",
      color = nextcord.Colour(0xFF0000)
    ))
  else:
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    await ctx.reply(embed = nextcord.Embed(
        title = "Ошибка:",
        description = exc,
        color = nextcord.Colour(0xFF0000)
    ))
    
@kgb.event
async def on_guild_join(guild: nextcord.Guild):
    url = on_guild_join_pic
    embed = nextcord.Embed(title = "Hello, comrades!", color = 0xff0000)
    embed.set_image(url = url)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed = embed)
            break
    embed = nextcord.Embed(title = "Я KGB Modern", description = "КГБ - Комитет Государственной Безопасности.\nЯ имею команды для модерации и развлечения.\nНапишите kgb!help чтобы увидеть полный список команд", color = 0x000000)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=embed)
            break
  
@kgb.command(description="Выведет список категорий или информацию о команде")
async def help(ctx, *, query=None):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return

    if query is None:
        if HELP_EMB is None:
            embed = nextcord.Embed(title='Системная ошибка:', description='Эмбед помощи не собран!', color=nextcord.Colour(0xFF0000))
            await ctx.send(embed=embed)
            return
        
        await ctx.send(embed=HELP_EMB)
        return

    if query.isdigit():
        if HELP_CAT_EMB is None:
            embed = nextcord.Embed(title="Системная ошибка:", description="Эмбед помощи категорий не собран!", color=nextcord.Colour(0xFF0000))
            await ctx.send(embed=embed)
            return

        try:
            if int(query) < 1: raise IndexError

            await ctx.send(embed=HELP_CAT_EMB[int(query) - 1])
            return
        except IndexError:
            embed = nextcord.Embed(title="Ошибка:", description="Неверный номер категории.", color=nextcord.Colour(0xFF0000))
            await ctx.send(embed=embed)
            return

    try:
        if not HELP_CAT_HIDDEN is None:
            await ctx.send(embed=HELP_CAT_HIDDEN[query])
            return
    except KeyError:
        pass

    command = kgb.get_command(query)
    if command is None:
        embed = nextcord.Embed(title="Ошибка:", description=f"Команда `{query}` не найдена.", color=nextcord.Colour(0xFF0000))
    else:
        embed = nextcord.Embed(title="Описание команды:", description=command.description, color=nextcord.Colour(0x000000))
        if command.aliases:
            aliases = ', '.join(command.aliases)
            embed.add_field(name="Альтернативные названия:", value=aliases, inline=False)
        usage = f"kgb!{command.name} {command.signature}"
        embed.add_field(name="Использование:", value=f"`{usage}`", inline=False)
    await ctx.send(embed=embed)

wiki = wikipediaapi.Wikipedia('ru')
  
@kgb.command(description = "Кот")
@helpCategory('api')
async def cat(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    response = requests.get("https://some-random-api.com/animal/cat")
    data = response.json()
    embed = nextcord.Embed(color=0x000000)
    embed.set_image(url=data['image'])
    embed.set_footer(text=data['fact'])
    await ctx.send(embed=embed)
  
@kgb.command(description = "Собака")
@helpCategory('api')
async def dog(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    response = requests.get('https://some-random-api.com/animal/dog')
    data = response.json()
    embed = nextcord.Embed(color=0x000000)
    embed.set_footer(text=data['fact'])
    embed.set_image(url=data["image"])
    await ctx.send(embed=embed)
  
@kgb.command(description = "Лис")
@helpCategory('api')
async def fox(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    response = requests.get("https://some-random-api.com/animal/fox")
    data = response.json()
    embed = nextcord.Embed(color=0x000000)
    embed.set_image(url=data["image"])
    embed.set_footer(text=data['fact'])
    await ctx.send(embed=embed)
  
@kgb.command(description = "Выключает бота(только для разработчика)")
@helpCategory('secret')
async def killbot(ctx):
  if isinstance(ctx.channel, nextcord.DMChannel):
     return
  if ctx.author.id == 745674921774153799:
    await ctx.send(embed = nextcord.Embed(
      title = 'Пожалуйста подождите:',
      description = "Бот выключиться через 3 секунды!",
      color = nextcord.Colour(0x000000)
    ))
    await asyncio.sleep(3)
    await kgb.close()
  else:
    await ctx.send(embed = nextcord.Embed(
      title = 'Ошибка:',
      description = "Эта команда только для разработчиков!",
      color = nextcord.Colour(0xFF0000)
    ))
    
@kgb.command(description = "Выводит шуточное сообщение о: \nУспешном/неуспешном взломе пользователя")
@helpCategory('fun')
async def hack(ctx, *, member):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    rand = random.randint(1,2)
    if rand == 1:
        await ctx.send(embed = nextcord.Embed(
          title = "Результат взлома:",
          description = f"{member} был успешно взломан!",
          color = nextcord.Color(0x000000)
        ))
    else:
        await ctx.send(embed = nextcord.Embed(
          title = "Результат взлома:",
          description = f"{member} не был взломан!",
          color = nextcord.Color(0x000000)
        ))
      
@kgb.command(description = "Гадальный шар")
@helpCategory('fun')
async def ball(ctx, *, question):
  if isinstance(ctx.channel, nextcord.DMChannel):
    return
  answers = ["Да", "Может быть", "Конечно", "Я не знаю", "Определённо **Нет**", "Нет", "Невозможно"] 
  await ctx.send(embed = nextcord.Embed(
    title = f"Вопрос: {question}",
    description = f"Ответ: {random.choice(answers)}",
    color = nextcord.Color(0x000000)
  ))
  
@kgb.command(description = "Бан пользователя")
@commands.has_permissions(ban_members=True)
@helpCategory('moderation')
async def ban(ctx, member: nextcord.Member = None, time=None, *, reason: str = None):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    if member == '1061907927880974406':
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description="Нет, сэр",
          color=nextcord.Color(0xFF0000)
        ))
      
    if member is None:
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description="Вы не указали кого нужно забанить!",
          color=nextcord.Color(0xFF0000)
        ))
    elif member.id == kgb.user.id:
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description="No, sir",
          color=nextcord.Color(0xFF0000)
        ))
    elif member.top_role >= ctx.author.top_role:
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description="Вы не можете забанить пользователя т.к. он выше вас по роли",
          color=nextcord.Color(0xFF0000)
        ))
    else:
        await member.ban(reason=reason)
        await ctx.send(embed=nextcord.Embed(
          title="Успешно:",
          description=f"Пользователь {member.name} был забанен",
          color=nextcord.Color(0x000000)
        ))
      
@kgb.command(description = "Покажет всех забаненных пользователей этого сервера")
@commands.has_permissions(ban_members = True)
@helpCategory('moderation')
async def banlist(ctx):
  if isinstance(ctx.channel, nextcord.DMChannel):
     return
  banned_users = ctx.guild.bans()
  banlist = []
  async for ban_entry in banned_users:
    banlist.append(f"{ban_entry.user.name}#{ban_entry.user.discriminator}\n")
  if banlist == []:
    await ctx.send(embed=nextcord.Embed(
      title="Банлист:",
      description = "На этом сервере нет забаненных пользователей.",
      color = nextcord.Color(0x000000)
    ))
  else:
    s = ''.join(banlist)
    await ctx.send(embed=nextcord.Embed(
      title = "Банлист:", 
      description = s, 
      color = nextcord.Color(0x000000)
    ))
    
@kgb.command(description = "Разбан пользователя")
@commands.has_permissions(ban_members = True)
@helpCategory('moderation')
async def unban(ctx, *, member):
  if isinstance(ctx.channel, nextcord.DMChannel):
    return
  banned_users = ctx.guild.bans()
  member_name, member_discriminator = member.split("#")
  async for ban_entry in banned_users:
    user = ban_entry.user
    if (user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(embed = nextcord.Embed(
        title = "Успешно:",
        escription=  f'Пользователь {user.name}#{user.discriminator} был разбанен',
        color = nextcord.Color(0x000000)
      ))
      
@kgb.command(description = "Удаляет сообщения")
@helpCategory('moderation')
async def clear(ctx, amount: int):
  if isinstance(ctx.channel, nextcord.DMChannel):
    return
  if ctx.author.guild_permissions.administrator:
    await ctx.channel.purge(limit = amount)
    await ctx.send(embed = nextcord.Embed(
      title = "Успешно",
      description = f'Успешно удалено {amount} сообщений',
      color = nextcord.Color(0x000000)
    ))
  else:
    await ctx.send(embed = nextcord.Embed(
        title = "Ошибка:",
        description = "Вы не имеете прав администратора!",
        color = nextcord.Color(0xFF0000)
    ))
    
@kgb.command(description = "Кик пользователя")
@commands.has_permissions(kick_members=True)
@helpCategory('moderation')
async def kick(ctx, member: nextcord.Member = None, *, reason:str =None):
  if isinstance(ctx.channel, nextcord.DMChannel):
    return
  if member.id == '1061907927880974406':
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description="Нет, сэр.",
          color=nextcord.Color(0xFF0000)
        ))
  if member is None:
    await ctx.send(embed = nextcord.Embed(
    title = "Ошибка:",
    description = "Вы должны указать кого кинуть!",
    color = nextcord.Color(0xFF0000)
    ))
  if member.top_role >= ctx.author.top_role:
    await ctx.send(embed=nextcord.Embed(
      title="Ошибка:",
      description="Вы не можете кикнуть пользователя т.к. он выше вас по ролям.",
      color=nextcord.Color(0xFF0000)
    ))
  elif member == kgb.user.id:
    await ctx.send(embed = nextcord.Embed(
      title = "Ошибка:",
      description = "Нет, сэр",
      color = nextcord.Color(0xFF0000)
    ))
  else:
    await member.kick(reason=reason)
    await ctx.send(embed = nextcord.Embed(
      title = "Успешно",
      description = f"Пользователь {member.name} был кикнут.",
      color = nextcord.Color(0x000000)
    ))
    
@kgb.command(description = "Покажет список версий бота" )
@helpCategory('secret')
async def verlist(ctx):
  if isinstance(ctx.channel, nextcord.DMChannel):
    return
  await ctx.send(embed = nextcord.Embed(
    title = "Список версий:",
    description = ver,
    color = nextcord.Color(0x000000)
  ))
  
@kgb.command(description = ")")
@helpCategory('secret')
async def love(ctx):
  if isinstance(ctx.channel, nextcord.DMChannel):
    return
  await ctx.send(embed = nextcord.Embed(
    title = "Да)",
    description = "Несо и Саня пара навеки:3",
    color = nextcord.Color(0xff7089)
  ))
  
@kgb.command(description = "шифр")
@helpCategory('misc')
async def cipher(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    url1 = cipherURL
    response1 = requests.get(url1)
    if response1.status_code != 200:
        await ctx.send('Ошибка загрузки изображения')
        return
    embed = nextcord.Embed(color=0x000000)
    embed.set_image(url=url1)
    await ctx.author.send(embed=embed)
    black_embed = nextcord.Embed(color=0x000000, description="20-9-23-5")
    await ctx.author.send(embed=black_embed)
  
@kgb.command(description = "Создаёт фейковый ютуб комментарий")
@helpCategory('api')
async def comment(ctx, *, commint):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    try:
        comm = commint.replace("\n", " ").replace("+", "%2B").replace(" ", "+")
    except:
        pass
    async with ctx.typing():
        async with aiohttp.ClientSession() as trigSession:
            async with trigSession.get(f'https://some-random-api.com/canvas/youtube-comment?avatar={ctx.author.avatar.url}&comment={(comm)}&username={ctx.author.name}') as trigImg:
                imageData = io.BytesIO(await trigImg.read())
                await trigSession.close()
                await ctx.send(embed=nextcord.Embed(
                  title="Ваш коммент:",
                  description="",
                  color=nextcord.Color(0x000000)
                ).set_image(url="attachment://youtube_comment.gif"), file=nextcord.File(imageData, 'youtube_comment.gif'))
              
@kgb.command(description = "Список благодарностей")
@helpCategory('misc')
async def thank(ctx):
  if isinstance(ctx.channel, nextcord.DMChannel):
    return
  await ctx.send(embed = nextcord.Embed(
    title = "Я благодарен:",
    description = "SvZ_Bonnie#5779, за предоставленный обучающий материал!\nGrisshink#6476, за помощь в разработке бота!\nSanechka#1384 за рисование аватара для бота и постоянную поддержку меня:3",
    color = nextcord.Color(0xffff00)
  ))
  
@kgb.command(description = "Даёт информацию о сервере")
@helpCategory('info')
async def server(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    guild = ctx.guild
    member_count = guild.member_count
    human_count = len([member for member in guild.members if not member.bot])
    bot_count = len([member for member in guild.members if member.bot])
    owner = guild.owner
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    created_at = guild.created_at.strftime("%d.%m.%Y %H:%M:%S")
    region = guild.preferred_locale
    embed = nextcord.Embed(title=f"Информация о сервере {guild.name}", color=0x000000)
    embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Участников:", value=member_count, inline=True)
    embed.add_field(name="Людей:", value=human_count, inline=True)
    embed.add_field(name="Ботов:", value=bot_count, inline=True)
    embed.add_field(name="Владелец сервера:", value=owner, inline=False)
    embed.add_field(name="Дата создания сервера:", value=created_at, inline=True)
    embed.add_field(name="Всего текстовых каналов:", value=text_channels, inline=True)
    embed.add_field(name="Всего войс каналов:", value=voice_channels, inline=True)
    embed.add_field(name="Регион сервера:", value=region, inline=True)
    await ctx.send(embed=embed)
  
@kgb.command(description="Задает канал для приветствия пользователей\n(написать в канал куда будут отправляться приветствия)\nЕсли хотите выключить приветственное сообщение, \nТо в качестве аргумета напишите: off")
@commands.has_permissions(administrator=True)
@helpCategory('config')
async def welcome(ctx, *, arg=None):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return
    guild_id = str(ctx.guild.id)
    if arg == "off":
        channels.pop(guild_id, None)
        with open("data/channels.json", "w") as f:
            json.dump(channels, f)
        await ctx.send(embed=nextcord.Embed(
            title="Приветствия выключены:",
            description="Теперь они больше не буду присылаться в этот канал.",
            color=nextcord.Color(0x000000)
        ))
    else:
        channel_id = str(ctx.channel.id)
        channels[guild_id] = channel_id
        with open("data/channels.json", "w") as f:
            json.dump(channels, f)
        await ctx.send(embed=nextcord.Embed(
            title="Приветствия включены:",
            description=f"Приветственные сообщения теперь буду присылаться в этот канал: \n{ctx.channel.mention}",
            color=nextcord.Color(0x000000)
        ))
  
@kgb.command(description = "Покажет аватар пользователя")
@helpCategory('info')
async def avatar(ctx, user: nextcord.User=None):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    server = ctx.author.guild
    if not user:
        user = ctx.message.author
    if server.get_member(user.id):
        user = server.get_member(user.id)
        userColor = user.colour
    else:
        userColor = 0x0000000
    embed=nextcord.Embed(title=f"Аватар {no_format(user)}", color=userColor)
    embed.set_image(url=user.avatar.url)
    await ctx.send(embed=embed)
  
@kgb.command(description = "Даёт информацию о пользователе")
@helpCategory('info')
async def user(ctx, member: nextcord.Member):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    status = str(member.status)
    tag = member.name + "#" + member.discriminator
    created_at = member.created_at.strftime("%d.%m.%Y %H:%M:%S")
    joined_at = member.joined_at.strftime("%d.%m.%Y %H:%M:%S")
    is_bot = "Это аккаунт бота" if member.bot else "Это аккаунт человека"
    is_admin = "Администратор сервера" if member.guild_permissions.administrator else "Это не администратор сервера"
    member_id = member.id
    avatar_url = member.avatar.url
    embed = nextcord.Embed(title="Информация о пользователе:", color=0x000000)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="статус:", value=status, inline=True)
    embed.add_field(name="Тэг:", value=tag, inline=True)
    embed.add_field(name="Дата создания аккаунта:", value=created_at, inline=False)
    embed.add_field(name="Дата приода на сервер:", value=joined_at, inline=True)
    embed.add_field(name="Тип аккаунта:", value=is_bot, inline=False)
    embed.add_field(name="Роль на сервере:", value=is_admin, inline=False)
    embed.add_field(name="Айди:", value=member_id, inline=False)
    await ctx.send(embed=embed)
  
@kgb.command(description = "Подбросит монетку")
@helpCategory('fun')
async def coin(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    result = random.choice(["орёл", "решка"])
    await ctx.send(embed = nextcord.Embed(
          title = "Результат:",
          description = f"Монетка показывает: **{result}**!",
          color = nextcord.Color(0x000000)
        ))
  
@kgb.command(description = "Выдаст предупреждение пользователю")
@commands.has_permissions(administrator=True)
@helpCategory('moderation')
async def warn(ctx, member: nextcord.Member, count: int=1):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
  
    if member.top_role >= ctx.author.top_role:
      await ctx.send(embed=nextcord.Embed(
        title="Ошибка:",
        description="Вы не можете выдать пользователю предупредение с большей или равной ролью, чем у вас.",
        color=nextcord.Color(0xFF0000)
     ))

    if user_id == '1061907927880974406':
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description="Нет, сэр",
          color=nextcord.Color(0xFF0000)
        ))
        return

    with open('data/warn.json', 'r') as f:
        warns = json.load(f)

    if guild_id not in warns:
        warns[guild_id] = {}

    if user_id not in warns[guild_id]:
        warns[guild_id][user_id] = count
    else:
        warns[guild_id][user_id] += count


    total_warns = warns[guild_id][user_id]

    with open('data/stanwarns.json', 'r') as f:
        stanwarns = json.load(f)

    if guild_id not in stanwarns:
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description='Условия кика и/или бана не настроены.\nУстановите их с помощью команды:\n`kgb!configwarn`',
          color=nextcord.Color(0xFF0000)
        ))
        return

    guild_stanwarns = stanwarns[guild_id]
    
    warn_type = guild_stanwarns.get('warn_type')
    warn_limit = guild_stanwarns.get('warn_limit')

    if total_warns >= warn_limit:
        if warn_type == 'kick':
            await member.kick()
            await ctx.send(embed = nextcord.Embed(
          title = "Кик:",
          description = f'{member.name} был кикнут. \nДостигнут лимит предупреждений: {total_warns}/{warn_limit}',
          color = nextcord.Color(0x000000)
        ))
            return

        if warn_type == 'ban':
            await member.ban(reason=f'Достигнут лимит предупреждений: {total_warns}/{warn_limit}')
            await ctx.send(embed = nextcord.Embed(
              title = "Бан:",
              description = f'{member.name} был забанен. \nДостигнут лимит предупреждений: {total_warns}/{warn_limit}',
              color = nextcord.Color(0x000000)
            ))

            del warns[guild_id][user_id]
            with open('data/warn.json', 'w') as f: 
                json.dump(warns, f)
            return

        await ctx.send(embed=nextcord.Embed(
          title="Конуз:",
          description=f'Невозможно произвести кик или бан {member.name}, т.к. указан неверный тип в configwarn',
          color=nextcord.Color(0xFF0000)
        ))

    with open('data/warn.json', 'w') as f: 
        json.dump(warns, f)

    await ctx.send(embed = nextcord.Embed(
              title = "Выдано предупреждение:",
              description = f'{member.mention} получил {count} предупреждение,\nТеперь он имеет {total_warns} предупреждений на этом сервере.',
              color = nextcord.Color(0x000000)
            ))

@kgb.command(description = "Снимет предупреждение пользователя")
@commands.has_permissions(administrator=True)
@helpCategory('moderation')
async def unwarn(ctx, member: nextcord.Member, count: int = 1):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    guild = str(ctx.guild.id)
    user = str(member.id)
  
    if user == '1061907927880974406':
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description="Нет, сэр",
          color=nextcord.Color(0xFF0000)
        ))
        return
      
    with open('data/stanwarns.json', 'r') as f:
        stanwarns = json.load(f)

    if guild not in stanwarns:
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description='Не установлены условия для предупреждений\nУстановите с помощью команды:\n`kgb!configwarn`',
          color=nextcord.Color(0xFF0000)
        ))
        return

    with open('data/warn.json', 'r') as f:
        warns = json.load(f)

    if guild not in warns:
        await ctx.send(embed=nextcord.Embed(
          title="Нет предупреждений:",
          description=f'У {member.mention} нет предупреждений на этом сервере.',
          color=nextcord.Color(0x000000)
        ))
        return

    if user not in warns[guild]:
        await ctx.send(embed=nextcord.Embed(
          title="Нет предупреждений:",
          description=f'У {member.mention} нет предупреждений на этом сервер.',
          color=nextcord.Color(0x000000)
        ))
        return

    if count > warns[guild][user]:
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description=f'У {member.mention} всего {warns[user][str(guild)]} предупреждений на этом сервере, вы не можете снять больше чем у него есть.',
          color=nextcord.Color(0xFF0000)
        ))
        return

    warns[guild][user] -= count
    total_warns = warns[guild][user]

    with open('data/warn.json', 'w') as f:
        json.dump(warns, f)

    await ctx.send(embed = nextcord.Embed(
              title = "Снято предупреждени(е/и):",
              description = f'{count} предупреждений успешно снято у {member.mention}. \nОсталось {total_warns} предупреждени(й/я/е) на этом сервере.',
              color = nextcord.Color(0x000000)
            ))

@kgb.command(description = "Покажет сколько предупреждений у пользователя")
@commands.has_permissions(administrator=True)
@helpCategory('moderation')
async def warnings(ctx, member: nextcord.Member):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    guild = str(ctx.guild.id)
    user = str(member.id)
    
    if user == '1061907927880974406':
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description="Нет, сэр",
          color=nextcord.Color(0xFF0000)
        ))
        return

    with open('data/warn.json', 'r') as f:
        warns = json.load(f)
    
    with open('data/stanwarns.json', 'r') as f:
        stanwarns = json.load(f)

    if guild not in stanwarns:
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description='Не установлены условия для предупреждений\nУстановите с помощью команды:\n`kgb!configwarn`',
          color=nextcord.Color(0xFF0000)
        ))
        return

    if guild not in warns:
        await ctx.send(embed = nextcord.Embed(
              title = "Ошибка:",
              description = 'На этом сервере не выдавалось никаких предупреждений',
              color = nextcord.Color(0x000000)
            ))
        return

    if user not in warns[guild]:
        await ctx.send(embed = nextcord.Embed(
              title = "Ошибка:",
              description = f'{member.display_name} не имеет предупреждений на этом сервере.',
              color = nextcord.Color(0x000000)
            ))
        return

    total_warns = warns[guild][user]
    await ctx.send(embed = nextcord.Embed(
              title = "Всего предупреждений:",
              description = f'{member.display_name} имеет {total_warns} предупреждений на этом сервере.',
              color = nextcord.Color(0x000000)
            ))

@kgb.command(description = "Установит лимит предупреждений и действия после него")
@commands.has_permissions(administrator=True)
@helpCategory('config')
async def configwarn(ctx, limit: int, warn_type: str):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    guild_id = str(ctx.guild.id)

    with open('data/stanwarns.json', 'r') as f:
        stanwarns = json.load(f)

    if guild_id not in stanwarns:
        stanwarns[guild_id] = {}

    if warn_type.lower() == 'kick':
        stanwarns[guild_id]['warn_type'] = 'kick'
        stanwarns[guild_id]['warn_limit'] = limit
    elif warn_type.lower() == 'ban':
        stanwarns[guild_id]['warn_type'] = 'ban'
        stanwarns[guild_id]['warn_limit'] = limit
    else:
        await ctx.send(embed=nextcord.Embed(
          title="Ошибка:",
          description='Неверный тип предупреждения. Доступны "kick" и "ban".',
          color=nextcord.Color(0xFF0000)
        ))
        return

    with open('data/stanwarns.json', 'w') as f:
        json.dump(stanwarns, f)

    await ctx.send(embed = nextcord.Embed(
              title = "Действие и лимит установлен:",
              description = f'Для сервера {ctx.guild.name} установлено {warn_type} при {limit} предупреждениях.',
              color = nextcord.Color(0x000000)
            ))

@kgb.command(description="Ищет пользователей по их примерному нику на всех серверах, где присутствует бот")
@helpCategory('info')
async def seek_user(ctx, *, query):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return
    users_found = set()
    for guild in kgb.guilds:
        for member in guild.members:
            if query.lower() in member.display_name.lower() or query.lower() in member.name.lower():
                users_found.add(f"{member.name}")

    if not users_found:
        await ctx.send(embed=nextcord.Embed(
            title="Ошибка:",
            description=f"Не могу найти пользователя по запросу '{query}'",
            color=nextcord.Color(0xFF0000)
        ))
    else:
        message = "\n".join(users_found)
        users_count = f"Найдено пользователей: {len(users_found)}"
        await ctx.send(embed=nextcord.Embed(
            title="Найденные пользователи:",
            description=f"{message}\n\n{users_count}",
            color=nextcord.Color(0x000000)
        ))

@kgb.command(description="Ищет сервер, на котором находится пользователь по его точному нику, на всех серверах где присутствует бот ")
@helpCategory('info')
async def seek_server(ctx, *, user_name):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    guild_seek = None
    with open(GUILD_SEEK_FILENAME, "r", encoding="utf-8") as f:
        guild_seek = json.load(f)

    found_servers = []
    count = 0  
    for guild_id, guild_info in guild_seek.items():
        for user in guild_info['users']:
            if user_name.lower() == f"{user['name']}".lower():
                guild = kgb.get_guild(int(guild_id))
                found_servers.append(guild.name)
                count += 1

    if not found_servers:
        await ctx.send(embed=nextcord.Embed(
            title="Ошибка:",
            description=f"Не могу найти сервер, на котором находится пользователь {user_name}",
            color=nextcord.Color(0xFF0000)
        ))
    else:
        message = "\n".join(found_servers)
        message_count = f"Всего найдено серверов: {count}"
        await ctx.send(embed=nextcord.Embed(
            title="Вот сервера на которых есть пользователь:",
            description=f"{message}\n\n{message_count}",
            color=nextcord.Color(0x000000)
        ))
      
@kgb.command(description = "Покажет пинг бота")
@helpCategory('misc')
async def ping(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    latency = kgb.latency
    await ctx.send(embed=nextcord.Embed(
            title="Понг!",
            description=f'Скорость: {latency*1000:.2f} мс',
            color=nextcord.Color(0x000000)
        ))

@kgb.command(description="Выведет рандомное число")
@helpCategory('fun')
async def rand(ctx, num1, num2=None):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    if num2 is None:
        num2 = num1
        num1 = 0
    try:
        num1, num2 = int(num1), int(num2)
    except ValueError:
        await ctx.send("Введите число(а)")
    else:
        if num1 >= num2:
            await ctx.send("Первое число должно быть меньше второго")
        else:
            result = random.randint(num1, num2)
            await ctx.send(embed=nextcord.Embed(
            title="Результат:",
            description=result,
            color=nextcord.Color(0x000000)
        ))

@kgb.command(description='Ищет статью на вики')
@helpCategory('api')
async def wiki(ctx, *, query):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    wikipedia.set_lang('ru')
    try:
        page = wikipedia.page(query)
        await ctx.send(embed=nextcord.Embed(
            title="Найдена страница",
            description=page.url,
            color=nextcord.Color(0x000000)
        ))
    except wikipedia.exceptions.PageError:
        await ctx.send(embed=nextcord.Embed(
            title="Ошибка:",
            description=f'Страница на Википедии не найдена для "{query}"',
            color=nextcord.Color(0xFF0000)
        ))
    except wikipedia.exceptions.DisambiguationError as e:
        await ctx.send(embed=nextcord.Embed(
            title="Ошибка:",
            description=f'Слишком много результатов для "{query}". Пожалуйста, уточните свой запрос.',
            color=nextcord.Color(0xFF0000)
        ))

@kgb.command(description = ")")
@helpCategory('secret')
async def hentai(ctx):
  if isinstance(ctx.channel, nextcord.DMChannel):
    return
  await ctx.send(embed = nextcord.Embed(
    title = "Не-а)",
    description = "Эй школьник, домашку сделай а потом дрочи)",
    color = nextcord.Color(0xff0000)
  ))

@kgb.command(description="Поцеловать участника")
@helpCategory('rp')
async def kiss(ctx, member: nextcord.Member):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    await ctx.send(f"{ctx.author.mention} поцеловал(а) {member.mention}")

@kgb.command(description="Обнять участника")
@helpCategory('rp')
async def hug(ctx, user: nextcord.Member):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return

    response = requests.get("https://some-random-api.com/animu/hug")
    data = response.json()
    image_url = data["link"]

    embed = nextcord.Embed()
    embed.set_image(url=image_url)
    embed.description = f"{ctx.author.mention} обнял(a) {user.mention}"
    embed.color=0x000000 
    await ctx.send(embed=embed)

@kgb.command(description="Ударить участника")
@helpCategory('rp')
async def hit(ctx, user: nextcord.Member):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    await ctx.send(f"{ctx.author.mention} ударил(а) {user.mention}")

@kgb.command(description="Лизнуть участника")
@helpCategory('rp')
async def lick(ctx, user: nextcord.Member):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    await ctx.send(f"{ctx.author.mention} лизнул(а) {user.mention}")

@kgb.command(description="Погладить участника")
@helpCategory('rp')
async def pet(ctx, member: nextcord.Member):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return

    response = requests.get("https://some-random-api.com/animu/pat")
    data = response.json()
    image_url = data["link"]

    embed = nextcord.Embed()
    embed.set_image(url=image_url)
    embed.description = f"{ctx.author.mention} погладил(а) {member.mention}"
    embed.color=0x000000
    await ctx.send(embed=embed)

@kgb.command(description="Поприветствовать участника")
@helpCategory('rp')
async def hi(ctx, member: nextcord.Member):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    await ctx.send(f'{ctx.author.mention} поприветствовал(а) {member.mention}')

@kgb.command(description='Вызывает голосование в канале\n(принимает длительность голосования только в часах)' )
@helpCategory('moderation')
async def poll(ctx, hours: int, *, text=None):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    if text is None:
        embedVar = nextcord.Embed(
          title='Ошибка:', 
          description='Пожалуйста, укажите текст!', 
          color=0xff0000
        )
        await ctx.reply(embed=embedVar, mention_author=False)
    
    end_time = datetime.utcnow() + timedelta(hours=hours)
    end_time_msk = end_time + timedelta(hours=3)
    end_time_str = end_time_msk.strftime('%H:%M:%S')
    
    embedVar = nextcord.Embed(
      title=f'Голосование от {ctx.author.name}', 
      description=f'{text}\n\n🔼 - Да\n🔽 - Нет\n\nГолосование закончится в {end_time_str} по МСК', 
      color=0x000000)
  
    await ctx.message.delete()
    msgp = await ctx.send(embed=embedVar)
    await msgp.add_reaction('🔼')
    await msgp.add_reaction('🔽')
    
    while datetime.utcnow() < end_time:
        await asyncio.sleep(1)
    
    msgp = await msgp.channel.fetch_message(msgp.id)
    results = msgp.reactions
    yes_votes = results[0].count - 1
    no_votes = results[1].count - 1
    embedVar = nextcord.Embed(
      title='Голосование завершено!', 
      description=f'{text}\n\n🔼 - Да ({yes_votes})\n🔽 - Нет ({no_votes})', 
      color=0x000000
    )
    await msgp.edit(embed=embedVar)

@kgb.command(description="Пишет информацию о категории\n(указывайте айди категории или её пинг")
@helpCategory('info')
async def category(ctx, category: nextcord.CategoryChannel):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    em = nextcord.Embed(title="Информация о категории:", color=0x000000)
    em.set_thumbnail(url=ctx.guild.icon.url)
    em.add_field(name="Имя:", value=category.name, inline=False)
    em.add_field(name="Создана:", value=category.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
    em.add_field(name="ID:", value=category.id, inline=False)
    em.add_field(name="Позиция:", value=category.position, inline=False)
    em.add_field(name="Количество каналов:", value=len(channels), inline=False)
    await ctx.send(embed=em)
  
@kgb.command(description="Пишет информацию о канале\n(указывайте айди канала или его пинг)")
@helpCategory('info')
async def channel(ctx, channel: typing.Optional[nextcord.TextChannel]):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    channel = channel or ctx.channel
    em = nextcord.Embed(title="Информация о канале:", color=0x000000)
    em.set_thumbnail(url=ctx.guild.icon.url)
    em.add_field(name="Имя:", value=channel.name, inline=False)
    em.add_field(name="Топик:", value=channel.topic or "Нет топика.", inline=False)
    em.add_field(name="Категория:", value=channel.category.name if channel.category else "Нет категории", inline=False)
    em.add_field(name="Позиция:", value=channel.position, inline=False)
    em.add_field(name="NSFW:", value=channel.is_nsfw(), inline=False)
    em.add_field(name="Слоумод:", value=channel.slowmode_delay, inline=False)
    em.add_field(name="Тип канала:", value=str(channel.type).capitalize(), inline=False)
    em.add_field(name="Создан:", value=channel.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
    await ctx.send(embed=em)
  
@kgb.command(description="Пишет информацию о роли\n(указывайте айди роли или её пинг" )
@helpCategory('info')
async def role(ctx, *, role: nextcord.Role):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    em = nextcord.Embed(title="Информация о роли:", color=0x000000)
    em.set_thumbnail(url=ctx.guild.icon.url)
    em.add_field(name="Имя:", value=role.name, inline=False)
    em.add_field(name="ID:", value=role.id, inline=False)
    em.add_field(name="Создана:", value=role.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
    em.add_field(name="Участников с этой ролью:", value=len(role.members), inline=False)
    em.add_field(name="Позиция:", value=role.position, inline=False)
    em.add_field(name="Показывается ли она отдельно:", value=role.hoist, inline=False)
    await ctx.send(embed=em)

@kgb.command(description="Выдаст рандомную цитату")
@helpCategory('fun')
async def quote(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    fortun = fortune.get_random_fortune('static_data/fortune')
    await ctx.send(f"```{fortun}```")

@kgb.command(description="Выдаст рандомную шутку про Штирлица")
@helpCategory('fun')
async def shtr(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    shtr = fortune.get_random_fortune('static_data/shtirlitz')
    await ctx.send(f"```{shtr}```")

@kgb.command(description="0x00000000")
@helpCategory('secret')
async def null(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return
    embed = nextcord.Embed(title="NULL OF PROJECT", color=0x00000000)
    embed.set_image(url=secretURL)
    await ctx.reply(embed=embed)

@kgb.command(description="Хорни карта")
@helpCategory('api')
async def horny(ctx, member: nextcord.Member = None):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return
    member = member or ctx.author
    async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            async with session.get(
            f'https://some-random-api.com/canvas/horny?avatar={member.avatar.url}') as af:
                if 300 > af.status >= 200:
                    fp = io.BytesIO(await af.read())
                    file = nextcord.File(fp, "horny.png")
                    em = nextcord.Embed(
                        color=0xFFC0CB,
                    )
                    em.set_image(url="attachment://horny.png")
                    await ctx.send(embed=em, file=file)
                else:
                    await ctx.send('No horny :(')
                await session.close()

@kgb.command(description="hello comrade!")
@helpCategory('api')
async def comrade(ctx, member: nextcord.Member = None):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    member = member or ctx.author
    async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            async with session.get(
            f'https://some-random-api.com/canvas/overlay/comrade?avatar={member.avatar.url}') as af:
                if 300 > af.status >= 200:
                    fp = io.BytesIO(await af.read())
                    file = nextcord.File(fp, "comrade.png")
                    em = nextcord.Embed(
                      color=0xff0000,
                    )
                    em.set_image(url="attachment://comrade.png")
                    await ctx.send(embed=em, file=file)
                else:
                    await ctx.send('No horny :(')
                await session.close()

@kgb.command(description="Взлом пентагона")
@helpCategory('fun')
async def hackp(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    progress = 0
    while progress < 100:
        await ctx.send(f'Pentagon hack progress: {progress}%')
        time.sleep(1)
        progress += random.randint(1, 10)

    if progress >= 100:
        await ctx.send('Pentagon hack progress: 100%')
        time.sleep(1.5)

    if random.randint(1, 30) > 20:
        await ctx.send('Pentagon hack: Completed successfully.')
    else:
        await ctx.send('Pentagon hack: Failed.')

@kgb.command(description="Не может проигрывать музыку с ютуба\nМожет проигрывать только прямые ссылки на аудиофайлы")
@helpCategory('music')
async def playaudio(ctx, url):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    if not ctx.author.voice:
        await ctx.send("Вы должны быть подключены к голосовому каналу, чтобы воспроизвести музыку.")
        return
    channel = ctx.author.voice.channel
    voice_client = await channel.connect()

    try:
        ffmpeg_options = {
            'options': '-vn',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }

        voice_client.play(nextcord.FFmpegPCMAudio(url, **ffmpeg_options))
    except:
        pass

    while voice_client.is_playing():
        await asyncio.sleep(1)
    await asyncio.sleep(5)
    await voice_client.disconnect()

@kgb.command(description="Может проигрывать музыку только с ютуба")
@helpCategory('music')
async def play(ctx, url):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    if not ctx.author.voice:
        await ctx.send("Вы должны быть подключены к голосовому каналу, чтобы воспроизвести музыку.")
        return
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][3]['url']

        voice_client.play(nextcord.FFmpegPCMAudio(url2))
    except:
        pass

    await ctx.send(f"Проигрывается музыка в канале {voice_channel}.")
    while voice_client.is_playing():
        await asyncio.sleep(1)
    await asyncio.sleep(5)
    await voice_client.disconnect()

@kgb.command(description="Выгоняет бота из войс канала")
@helpCategory('music')
async def leave(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@kgb.command(description='Вышлет вам код дискорд бота "SudoBot"')
@helpCategory('misc')
async def code(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    file_path = 'static_data/sudocode.py'
    file = nextcord.File(file_path)
    await ctx.send(file=file)

@kgb.command(description='Введите эту команду в тот канал куда вы хотите получать новости.\nНапишите в качестве агрумента "Off" если хотите отписаться от новостей.')
@helpCategory('config')
async def sub(ctx, arg=None):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    channel_id = str(ctx.channel.id)

    if arg == 'off':
        remove_channel(channel_id)
        await ctx.send(f'Канал {ctx.channel.mention} удален из списка.')
    else:
        add_channel(channel_id)
        await ctx.send(f'Канал {ctx.channel.mention} добавлен в список.')

def add_channel(channel_id):
    with open('data/retr.txt', 'a') as file:
        file.write(channel_id + '\n')

def remove_channel(channel_id):
    with open('data/retr.txt', 'r') as file:
        channel_ids = file.readlines()

    with open('data/retr.txt', 'w') as file:
        for id in channel_ids:
            if id.strip() != channel_id:
                file.write(id)

@kgb.command(description="Выводит всю информацию о скрэтч-пользователе")
@helpCategory('scratch')
async def scratch_user(ctx, username):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return
    base_url = "https://api.scratch.mit.edu/users/"
    url = base_url + username

    try:
        response = requests.get(url)
        data = response.json()

        if 'username' in data:
            user_info = {
                "Страна:": data['profile']['country'],
                "Обо мне:": data['profile']['bio'],
                "Над чем я работаю": data['profile']['status'],
                "Дата создания аккаунта:": data['history']['joined'],
            }

            embed = nextcord.Embed(title=f"Информация о пользователе {username}", color=nextcord.Color.orange())
            for key, value in user_info.items():
                embed.add_field(name=key, value=value, inline=False)

            embed.set_thumbnail(url=data['profile']['images']['90x90']) 

            embed.set_footer(text=f"ID: {data['id']}")  

            await ctx.send(embed=embed)
        else:
            await ctx.send("Пользователь не найден.")
    except requests.exceptions.RequestException as e:
        print("Error:", e)

@kgb.command(description="Нейросеть которая рисует несуществующих людей")
@helpCategory('neuro')
async def person(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    image_url = 'https://thispersondoesnotexist.com'
    response = requests.get(image_url)

    await ctx.send(file=nextcord.File(io.BytesIO(response.content), 'generated_image.jpg'))

@kgb.command(description="Интересное о Космосе")
@helpCategory('api')
async def nasa(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key":  nasaKEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    embed = nextcord.Embed(title=data['title'], description=data['explanation'], color=nextcord.Color.dark_blue())
    embed.set_image(url=data['url'])

    await ctx.send(embed=embed)

@kgb.command(description="Генератор оскарблений")
@helpCategory('api')
async def insult(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    url = "https://evilinsult.com/generate_insult.php?lang=ru&type=json"
    response = requests.get(url)
    data = response.json()

    insult = data['insult']

    await ctx.send(embed = nextcord.Embed(
          title = insult,
          description = "",
          color = nextcord.Color(0x000000)
        ))

@kgb.command(description="Генератор бреда Порфирьевич")
@helpCategory('neuro')
async def porfir(ctx, *, prompt):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    
    async def get():
        api_url = 'https://pelevin.gpt.dobro.ai/generate/'
        data = {
            'prompt': prompt,
            'length': random.randint(20, 60)
        }
        try:
            response = requests.post(api_url, json=data, timeout=30)
        except requests.ConnectTimeout:
            await ctx.reply(embed = nextcord.Embed(
                  title = 'Ошибка:',
                  description = 'Превышено время ожидания',
                  color = nextcord.Color(0xFF0000)
                ))
            return

        
        if response.status_code == 200:
            data = response.json()
            generated_text = data['replies'][0]
            await ctx.send(f'```\n{prompt}{generated_text}\n```')
            return
        if response.status_code == 500:
           await ctx.send(f"Нейросеть отключена, невозможно предположить время её включения.")
        else:
            await ctx.send(f"Произошла ошибка при получении данных от API Профирьевича. Код ошибки: {response.status_code}")

    async with ctx.typing():
        await get()

@kgb.command(description="Генератор бреда Балабоба")
@helpCategory('neuro')
async def balabola(ctx, *, prompt):
    if isinstance(ctx.channel, nextcord.DMChannel):
      return
    
    text_types = bb.get_text_types(language="ru")
    async def get():
        response = bb.balaboba(prompt, text_type=text_types[0])
        
        await ctx.send(f'```\n{response}\n```')

    async with ctx.typing():
        await get()

@kgb.command(description='Переведёт кириллицу в транслит или транслит в кириллицу')
@helpCategory('fun')
async def translit(ctx, option: str, lang_code: str, *, text: str):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return

    if option.lower() == 't':
        translit_text = transliterate.translit(text, lang_code, reversed=True)
        title = 'Перевод на транслит:'
    elif option.lower() == 'c':
        translit_text = transliterate.translit(text, lang_code, reversed=False)
        title = 'Перевод на кириллицу:'
    else:
        await ctx.send('Неправильно указана опция. Используйте "t" или "c".')
        return

    await ctx.send(embed=nextcord.Embed(
        title=title,
        description=translit_text,
        color=nextcord.Color(0x000000)
    ))

@kgb.command(description = "Перезапускает бота(только для разработчика)")
@helpCategory('secret')
async def reload(ctx):
  if isinstance(ctx.channel, nextcord.DMChannel): return

  if ctx.author.id == 745674921774153799 or ctx.author.id == 999606704541020200:
    await ctx.send(embed = nextcord.Embed(
      title = 'Пожалуйста подождите:',
      description = "Бот перезагрузится через 3 секунды!",
      color = nextcord.Colour(0x000000)
    ))
    await asyncio.sleep(3)
    exit(1)
    await kgb.close()
  else:
    await ctx.send(embed = nextcord.Embed(
      title = 'Ошибка:',
      description = "Эта команда только для разработчиков!",
      color = nextcord.Colour(0xFF0000)
    ))

@kgb.command(description="Генерирует текст как гена.\nДля того, чтобы бот работал в данном канале,\nПропишите: kgb!genconfig read true")
@helpCategory('neuro')
async def gen(ctx, *args: str):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return
    channelId = str(ctx.channel.id)
    if channelId not in genAiArray or not genAiArray[channelId].config['read']:
        await ctx.send(embed=nextcord.Embed(
                title="Ошибка:",
                description="Бот не может читать сообщения с этого канала! Включите это через команду `kgb!genconfig read true`!",
                color=nextcord.Colour(0xFF0000)
        ))
        return
    
    try:
        await ctx.send(genAiArray[channelId].generate(' '.join(args)[:2000]))
    except ValueError as exc:
        await ctx.send(embed=nextcord.Embed(
            title='Ошибка:',
            description=exc,
            color=nextcord.Colour(0xFF0000)
        ))

@kgb.command(description="Настраивает поведение команды kgb!gen в данном канале.\n Введите имя опции без значения, чтобы посмотреть её текущее значение.\nДоступные опции:\n`read true/false` - Позволяет боту сохранять сообщения и картинки для генерации\n`reply_on_mention true/false` - Позволяет боту генерировать текст если ответить на его сообщение\n`remove_mentions true/false` - Не позволяет упоминать участников в сгенерированном тексте")
@helpCategory('config')
async def genconfig(ctx, option: str, *, value: typing.Union[str, None] = None):
    optionKeys = ''.join([f'`{key}` ' for key in markov.DEFAULT_CONFIG])

    def strToBool(inp: str) -> bool: return inp.lower() == 'true'

    if isinstance(ctx.channel, nextcord.DMChannel): 
        await ctx.send(embed=nextcord.Embed(
            title='Ошибка:',
            description=f'Невозможно использовать kgb!genconfig в ЛС!',
            color=nextcord.Colour(0xFF0000)
        ))
        return
    
    channelId = str(ctx.channel.id)

    if channelId not in genAiArray:
        if value: genAiArray[channelId] = markov.MarkovGen()
        else:
            if option not in markov.DEFAULT_CONFIG:
                await ctx.send(embed=nextcord.Embed(
                    title='Ошибка:',
                    description=f'Неизвестное значение `{option}`! \nПожалуйста, пропишите команду:\n`kgb!help genconfig`',
                    color=nextcord.Colour(0xFF0000)
                ))
                return

            await ctx.send(embed=nextcord.Embed(
                title='Инфо',
                description=f'Значение `{option}` равно `{markov.DEFAULT_CONFIG[option]}`',
                color=nextcord.Colour(0x000000)
            ))
            return

    genAi = genAiArray[channelId]
    if option not in genAi.config:
        await ctx.send(embed=nextcord.Embed(
            title='Ошибка:',
            description=f'Неизвестное значение `{option}`! \nПожалуйста, пропишите команду:\n`kgb!help genconfig`',
            color=nextcord.Colour(0xFF0000)
        ))
        return

    if value:
        genAi.config[option] = strToBool(value)
        await ctx.send(embed=nextcord.Embed(
            title='Успешно',
            description=f'Значение `{option}` было установлено в `{genAi.config[option]}`',
            color=nextcord.Colour(0x000000)
        ))
    else: 
        await ctx.send(embed=nextcord.Embed(
            title='Инфо',
            description=f'Значение `{option}` равно `{genAi.config[option]}`',
            color=nextcord.Colour(0x000000)
        ))

@kgb.command(description="Удаляет все сообщения из базы генерации")
@helpCategory('config')
async def genclear(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel): 
        await ctx.send(embed=nextcord.Embed(
            title='Ошибка:',
            description='Невозможно использовать kgb!genclear в ЛС!',
            color=nextcord.Colour(0xFF0000)
        ))
        return

    if str(ctx.channel.id) in genAiArray:
        del genAiArray[str(ctx.channel.id)]

    await ctx.send(embed=nextcord.Embed(
        title='Успешно!',
        description='Все данные команды kgb!gen очищены в этом канале!',
        color=nextcord.Colour(0x000000)
    ))

@kgb.command(description="Выводит факты о числах(на англиском).\nДоступные типы фактов:\n`math` `date` `year` `trivia`")
@helpCategory('api')
async def factnumber(ctx, number: str, fact_type: str):
    if not number.isdigit():
        await ctx.send(embed=nextcord.Embed(
            title='Ошибка:',
            description="Пожалуйста, введите корректное число.",
            color=nextcord.Colour(0xFF0000)
        ))
        return
        
    valid_fact_types = ['trivia', 'math', 'date', 'year']
    if fact_type not in valid_fact_types:
        await ctx.send(embed=nextcord.Embed(
            title='Ошибка:',
            description="Пожалуйста, введите корректный тип факта.",
            color=nextcord.Colour(0xFF0000)
        ))
        return

    url = f"http://numbersapi.com/{number}/{fact_type}?lang=ru"
    response = requests.get(url)

    if response.status_code == 200:
        fact_text = response.text
        await ctx.send(embed=nextcord.Embed(
            title='Факт о числе:',
            description=fact_text,
            color=nextcord.Colour(0x000000)
        ))
    else:
        await ctx.send(embed=nextcord.Embed(
            title='Ошибка:',
            description=f"Извините, не удалось получить факт о числе {number}.",
            color=nextcord.Colour(0xFF0000)
        ))
        
@kgb.command(description="Нейросеть ChatGPT")
@helpCategory('neuro')
async def chat(ctx, *, message: str):
    print(g4f.Provider.Ails.params)
    response = g4f.ChatCompletion.create(model='gpt-3.5-turbo', provider=g4f.Provider.DeepAi, messages=[
        {"role": "user", "content": message}])
    
    await ctx.send(response)

@kgb.command(description="Гадает по имени")
@helpCategory('api')
async def name(ctx, *names):
    name_list = list(names)
    g = AsyncNameAPI(name_list, mode="*")
    result = await g.get_names_info()

    embed = nextcord.Embed(title="Информация о именах", color=nextcord.Color(0x000000))

    for name, info in result.items():
        age = info['age'] if info['age'] is not None else "Неизвестно"
        gender = info['gender'] if info['gender'] is not None else "Неизвестно"
        probability = info['probability']
        country_list = [f"{country['country_id']} ({country['probability']})" for country in info['country']]
        country = "\n".join(country_list)

        embed.add_field(name=name, value=f"Возраст: {age}\nПол: {gender}\nВероятность: {probability}\nСтраны:\n{country}", inline=False)

    await ctx.send(embed=embed)


@kgb.command(description="Создаёт демотиватор\nОн использует сохранёные картинки из чата,\nНо вы можете прикрепить изображение к сообщению что использовать его")
@helpCategory('neuro')
async def demotivator(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return
    channelId = str(ctx.channel.id)
    if channelId not in genAiArray or not genAiArray[channelId].config['read']:
        await ctx.send(embed=nextcord.Embed(
                title="Ошибка:",
                description="Бот не может читать сообщения с этого канала! Включите это через команду `kgb!genconfig read true`!",
                color=nextcord.Colour(0xFF0000)
        ))
        return
    
    try:
        attachment = ctx.message.attachments[0] if ctx.message.attachments else None
        if attachment and attachment.filename.endswith(('.png', '.jpg', '.jpeg')):
            random_image = await attachment.read()
        else:
            if channelId not in image_list or len(image_list[channelId]) == 0:
                await ctx.send(embed=nextcord.Embed(
                        title="Ошибка:",
                        description="Пожалуйста укажите картинку!",
                        color=nextcord.Colour(0xFF0000)
                ))
                return

            random_image_url = random.choice(image_list[channelId])
            response = requests.get(random_image_url)
            if response.status_code == 200:
                random_image = response.content
            else:
                await ctx.send(response.status_code)
                return
        with open("downloaded_image.jpg", "wb") as file:
            file.write(random_image)

        conf = demapi.Configure(
            base_photo="downloaded_image.jpg",
            title=genAiArray[channelId].generate(),
            explanation=genAiArray[channelId].generate()
        )
        image = await conf.coroutine_download()
        image.save("demotivator.png")
        
        await ctx.send(file=nextcord.File("demotivator.png"))
        os.remove("demotivator.png")
    
    except ValueError as exc:
        await ctx.send(embed=nextcord.Embed(
            title='Ошибка:',
            description=exc,
            color=nextcord.Colour(0xFF0000)
        ))

@kgb.command(description="Покажет всю информацию о боте")
@helpCategory('info')
async def bot_info(ctx):
    if isinstance(ctx.channel, nextcord.DMChannel):
        return
    embed = nextcord.Embed(title="Информация о боте:", description="КГБ - Комитет Государственной Безопасности\nНапишите kgb!help чтобы увидеть полный список команд\nБот очень активно разрабатывается, \nПоэтому может падать несколько раз в день", color=nextcord.Color(0x000000))
    embed.add_field(name="Версия:", value="3.0", inline=False)
    embed.add_field(name="Полезные ссылки:", value=f"[Добавить {kgb.user.name} на свой сервер]({botURL})\n[Присоединится к серверу бота]({serverURL})\n[Поддержать бота на бусти]({boostyURL})", inline=False)
    embed.set_thumbnail(url=tumbaYUMBA)
    embed.set_footer(text="© 2023 Soviet WorkShop", icon_url=avaURL)
    await ctx.send(embed=embed)

@kgb.slash_command(name = "hack", description="Взламывает пользователя (не по-настоящему)")
async def heck(interaction: Interaction, *, member):
     await interaction.send(embed = nextcord.Embed(
    description=f"{member} был успешно взломан!",
		color = 0x2F3136
	))

HELP_EMB = buildHelpEmbed()
HELP_CAT_EMB, HELP_CAT_HIDDEN = buildCategoryEmbeds()
kgb.run(getenv('DISCORD_TOKEN', ''))
