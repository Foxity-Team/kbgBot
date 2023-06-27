import discord
from discord.ext import commands
import discord.utils
from discord.ext.commands import BadArgument
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

from os import getenv
from dotenv import load_dotenv
from categories import buildHelpEmbed, buildCategoryEmbeds, helpCategory

prefix = ["kgb!", "$sudo ", "please, dear bot, take me a", "aid!"]
print("AdventurerUp Corporation")
kgb = commands.Bot(command_prefix = prefix, strip_after_prefix = True, sync_commands=True, intents = discord.Intents.all())
kgb.persistent_views_added = False
kgb.remove_command("help")
load_dotenv()

GUILD_SEEK_FILENAME = "data/guild_seek.json"

HELP_EMB: typing.Union[discord.Embed, None] = None
HELP_CAT_EMB: typing.Union[list[discord.Embed], None] = None

if not os.path.isfile('data/guild_seek.json'):
    with open('data/guild_seek.json', 'w', encoding='utf-8') as f:
        f.write('{}')

async def change_status():
    statuses = "kgb!help", "версия 2.5", "на {} серверах!", "SLAVA KPSS!"
    index = 0
    while not kgb.is_closed():
        servers_count = len(kgb.guilds)
        status = statuses[index].format(servers_count)
        await kgb.change_presence(activity=discord.Game(name=status))
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

def get_age(name):
    url = f"https://api.agify.io?name={name}"
    response = requests.get(url)
    data = response.json()
    age = data.get('age')
    return age

def get_nationality(name):
    url = f"https://api.nationalize.io?name={name}"
    headers = {'Authorization': f'Bearer {NATIONALIZE_API_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    nationality = data.get('country')[0].get('country_id')
    probability = data.get('country')[0].get('probability')
    return nationality, probability

def get_gender(name):
    url = f"https://api.genderize.io?name={name}"
    headers = {'Authorization': f'Bearer {GENDERIZE_API_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    gender = data.get('gender')
    probability = data.get('probability')
    return gender, probability

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
    if isinstance(user, discord.Member):
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
    print('Бот в полной боевой готовности!')
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
                embed = discord.Embed(
                    title=f'Сообщение из канала #{message.channel.name}:',
                    description=message.content,
                    color=discord.Color(int(embed_color, 16))
                )
                if len(message.attachments) > 0:
                    for attachment in message.attachments:
                        embed.set_image(url=attachment.url)
                await channel.send(embed=embed)
              
    if message.content == "<@1061907927880974406>":
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
    await ctx.reply(embed = discord.Embed(
      title = "Ошибка:",
      description = "Найдены некорректные аргументы",
      color = discord.Colour(0xFF0000)
    ))
  elif isinstance(exc, commands.CommandNotFound):
    cmd = ctx.invoked_with
    cmds = [cmd.name for cmd in kgb.commands]
    matches = get_close_matches(cmd, cmds)
    if len(matches) > 0:
      await ctx.reply(embed = discord.Embed(
        title = "Ошибка:",
        description = f"Команда `kgb!{cmd}` не найдена, может вы имели ввиду `kgb!{matches[0]}`?",
        color = discord.Colour(0xFF0000)
      ))
    else:
      return await ctx.reply(embed = discord.Embed(
        title = "Ошибка:",
        description = "Команда не найдена. \nПожалуйста, напишите `kgb!help` чтобы посмотреть полный список команд!", 
        color = discord.Colour(0xFF0000)
      ))
  elif isinstance(exc, commands.CommandOnCooldown):
    await ctx.reply(embed = discord.Embed(
      title = "Эта команда перезагружаеться!",
      description = f"Повторите попытку через {round(exc.retry_after, 2)} секунд.",
      color = discord.Colour(0xFF0000)
    ))
  elif isinstance(exc, commands.MissingPermissions):
    await ctx.reply(embed = discord.Embed(
      title = "Ошибка:", 
      description = "Вы не имеете прав администратора!", 
      color = discord.Colour(0xFF0000)
    ))
  elif isinstance(exc, commands.MissingRequiredArgument):
    await ctx.reply(embed = discord.Embed(
      title = "Ошибка:",
      description = f"Пропущен аргумент: `{exc.param.name}`!",
      color = discord.Colour(0xFF0000)
    ))
  else:
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    
@kgb.event
async def on_guild_join(guild: discord.Guild):
    url = "https://media.discordapp.net/attachments/1068579157493153863/1094662619211780096/Bez_nazvania2_20230409092059.png"
    embed = discord.Embed(title = "Hello, comrades!", color = 0xff0000)
    embed.set_image(url = url)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed = embed)
            break
    embed = discord.Embed(title = "Я KGB Modern", description = "КГБ - Комитет Государственной Безопасности.\nЯ имею команды для модерации и развлечения.\nНапишите kgb!help чтобы увидеть полный список команд", color = 0x000000)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=embed)
            break
  
@kgb.command(description="Выведет список команд или информацию о команде")
async def help(ctx, *, query=None):
    if isinstance(ctx.channel, discord.DMChannel):
        return

    if query is None:
        if HELP_EMB is None:
            embed = discord.Embed(title='Системная ошибка:', description='Эмбед помощи не собран!', color=discord.Colour(0xFF0000))
            await ctx.send(embed=embed)
            return
        
        await ctx.send(embed=HELP_EMB)
        return

    if query.isdigit():
        if HELP_CAT_EMB is None:
            embed = discord.Embed(title="Системная ошибка:", description="Эмбед помощи категорий не собран!", color=discord.Colour(0xFF0000))
            await ctx.send(embed=embed)
            return

        try:
            if int(query) < 1: raise IndexError

            await ctx.send(embed=HELP_CAT_EMB[int(query) - 1])
            return
        except IndexError:
            embed = discord.Embed(title="Ошибка:", description="Неверный номер категории.", color=discord.Colour(0xFF0000))
            await ctx.send(embed=embed)
            return

    command = kgb.get_command(query)
    if command is None:
        embed = discord.Embed(title="Ошибка:", description=f"Команда `{query}` не найдена.", color=discord.Colour(0xFF0000))
    else:
        embed = discord.Embed(title="Описание команды:", description=command.description, color=discord.Colour(0x000000))
        if command.aliases:
            aliases = ', '.join(command.aliases)
            embed.add_field(name="Альтернативные названия:", value=aliases, inline=False)
        usage = f"kgb!{command.name} {command.signature}"
        embed.add_field(name="Использование:", value=f"`{usage}`", inline=False)
    await ctx.send(embed=embed)
      
cyrillic = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
translit = "abvgdeejzijklmnoprstufhzcss_y_eua"
cyrillic_table = str.maketrans(cyrillic, translit)
translit_table = str.maketrans(translit, cyrillic)

wiki = wikipediaapi.Wikipedia('ru')
  
@kgb.command(description = "Кот")
@helpCategory('fun')
async def cat(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    response = requests.get("https://some-random-api.com/animal/cat")
    data = response.json()
    embed = discord.Embed(color=0x000000)
    embed.set_image(url=data['image'])
    embed.set_footer(text=data['fact'])
    await ctx.send(embed=embed)
  
@kgb.command(description = "Собака")
@helpCategory('fun')
async def dog(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    response = requests.get('https://some-random-api.com/animal/dog')
    data = response.json()
    embed = discord.Embed(color=0x000000)
    embed.set_footer(text=data['fact'])
    embed.set_image(url=data["image"])
    await ctx.send(embed=embed)
  
@kgb.command(description = "Лис")
@helpCategory('fun')
async def fox(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    response = requests.get("https://some-random-api.com/animal/fox")
    data = response.json()
    embed = discord.Embed(color=0x000000)
    embed.set_image(url=data["image"])
    embed.set_footer(text=data['fact'])
    await ctx.send(embed=embed)
  
@kgb.command(description = "Выключает бота(только для разработчика)")
@helpCategory('misc')
async def killbot(ctx):
  if isinstance(ctx.channel, discord.DMChannel):
     return
  if ctx.author.id == 745674921774153799:
    await ctx.send(embed = discord.Embed(
      title = 'Пожалуйста подождите:',
      description = "Бот выключиться через 3 секунды!",
      color = discord.Colour(0x000000)
    ))
    await asyncio.sleep(3)
    await kgb.close()
  else:
    await ctx.send(embed = discord.Embed(
      title = 'Ошибка:',
      description = "Эта команда только для разработчиков!",
      color = discord.Colour(0xFF0000)
    ))
    
@kgb.command(description = "Выводит шуточное сообщение о: \nУспешном/неуспешном взломе пользователя")
@helpCategory('fun')
async def hack(ctx, *, member):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    rand = random.randint(1,2)
    if rand == 1:
        await ctx.send(embed = discord.Embed(
          title = "Результат взлома:",
          description = f"{member} был успешно взломан!",
          color = discord.Color(0x000000)
        ))
    else:
        await ctx.send(embed = discord.Embed(
          title = "Результат взлома:",
          description = f"{member} не был взломан!",
          color = discord.Color(0x000000)
        ))
      
@kgb.command(description = "Гадальный шар")
@helpCategory('fun')
async def ball(ctx, *, question):
  if isinstance(ctx.channel, discord.DMChannel):
    return
  answers = ["Да", "Может быть", "Конечно", "Я не знаю", "Определённо **Нет**", "Нет", "Невозможно"] 
  await ctx.send(embed = discord.Embed(
    title = f"Вопрос: {question}",
    description = f"Ответ: {random.choice(answers)}",
    color = discord.Color(0x000000)
  ))
  
@kgb.command(description = "Бан пользователя")
@commands.has_permissions(ban_members=True)
@helpCategory('moderation')
async def ban(ctx, member: discord.Member = None, time=None, *, reason: str = None):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    if member == '1061907927880974406':
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description="Нет, сэр",
          color=discord.Color(0xFF0000)
        ))
      
    if member is None:
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description="Вы не указали кого нужно забанить!",
          color=discord.Color(0xFF0000)
        ))
    elif member.id == kgb.user.id:
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description="No, sir",
          color=discord.Color(0xFF0000)
        ))
    elif member.top_role >= ctx.author.top_role:
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description="Ты не можешь забанить пользователя т.к. он выше тебя по роли",
          color=discord.Color(0xFF0000)
        ))
    else:
        await member.ban(reason=reason)
        await ctx.send(embed=discord.Embed(
          title="Успешно:",
          description=f"Пользователь {member.name} был забанен",
          color=discord.Color(0x000000)
        ))
      
@kgb.command(description = "Покажет всех забаненных пользователей этого сервера")
@commands.has_permissions(ban_members = True)
@helpCategory('moderation')
async def banlist(ctx):
  if isinstance(ctx.channel, discord.DMChannel):
     return
  banned_users = ctx.guild.bans()
  banlist = []
  async for ban_entry in banned_users:
    banlist.append(f"{ban_entry.user.name}#{ban_entry.user.discriminator}\n")
  if banlist == []:
    await ctx.send(embed=discord.Embed(
      title="Банлист:",
      description = "На этом сервере нет забаненных пользователей.",
      color = discord.Color(0x000000)
    ))
  else:
    s = ''.join(banlist)
    await ctx.send(embed=discord.Embed(
      title = "Банлист:", 
      description = s, 
      color = discord.Color(0x000000)
    ))
    
@kgb.command(description = "Разбан пользователя")
@commands.has_permissions(ban_members = True)
@helpCategory('moderation')
async def unban(ctx, *, member):
  if isinstance(ctx.channel, discord.DMChannel):
    return
  banned_users = ctx.guild.bans()
  member_name, member_discriminator = member.split("#")
  async for ban_entry in banned_users:
    user = ban_entry.user
    if (user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(embed = discord.Embed(
        title = "Успешно:",
        escription=  f'Пользователь {user.name}#{user.discriminator} был разбанен',
        color = discord.Color(0x000000)
      ))
      
@kgb.command(description = "Удаляет сообщения")
@helpCategory('moderation')
async def clear(ctx, amount: int):
  if isinstance(ctx.channel, discord.DMChannel):
    return
  if ctx.author.guild_permissions.administrator:
    await ctx.channel.purge(limit = amount)
    await ctx.send(embed = discord.Embed(
      title = "Успешно",
      description = f'Успешно удалено {amount} сообщений',
      color = discord.Color(0x000000)
    ))
  else:
    await ctx.send(embed = discord.Embed(
        title = "Ошибка:",
        description = "Вы не имеете прав администратора!",
        color = discord.Color(0xFF0000)
    ))
    
@kgb.command(description = "Кик пользователя")
@commands.has_permissions(kick_members=True)
@helpCategory('moderation')
async def kick(ctx, member: discord.Member = None, *, reason:str =None):
  if isinstance(ctx.channel, discord.DMChannel):
    return
  if member.id == '1061907927880974406':
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description="Нет, сэр.",
          color=discord.Color(0xFF0000)
        ))
  if member is None:
    await ctx.send(embed = discord.Embed(
    title = "Ошибка:",
    description = "Вы должны указать кого кинуть!",
    color = discord.Color(0xFF0000)
    ))
  if member.top_role >= ctx.author.top_role:
    await ctx.send(embed=discord.Embed(
      title="Ошибка:",
      description="Вы не можете кикнуть пользователя т.к. он выше вас по ролям.",
      color=discord.Color(0xFF0000)
    ))
  elif member == kgb.user.id:
    await ctx.send(embed = discord.Embed(
      title = "Ошибка:",
      description = "Нет. сэр",
      color = discord.Color(0xFF0000)
    ))
  else:
    await member.kick(reason=reason)
    await ctx.send(embed = discord.Embed(
      title = "Успешно",
      description = f"Пользователь {member.name} был кикнут.",
      color = discord.Color(0x000000)
    ))
    
@kgb.command(description = "Покажет список версий бота" )
@helpCategory('misc')
async def verlist(ctx):
  if isinstance(ctx.channel, discord.DMChannel):
    return
  await ctx.send(embed = discord.Embed(
    title = "Список версий:",
    description = "0.1.0 \n0.2.0 \n0.3.0 \n0.4.0 \n0.5.0 \n0.6.0 \n0.6.3 \n0.6.4 \n1.0 \n1.1 \n1.2 \n1.2.5 \n1.3 \n1.5 \n1.5.5 \n1.6 \n1.7 \n1.8 \n2.0(нынешняя)",
    color = discord.Color(0x000000)
  ))
  
@kgb.command(description = ")")
async def love(ctx):
  if isinstance(ctx.channel, discord.DMChannel):
    return
  await ctx.send(embed = discord.Embed(
    title = "Да)",
    description = "Несо и Саня пара навеки:3",
    color = discord.Color(0xff7089)
  ))
  
@kgb.command(description = "шифр")
@helpCategory('misc')
async def cipher(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    url1 = 'https://media.discordapp.net/attachments/977992655466270730/1073628659417632828/qr-code.png?width=425&height=425'
    response1 = requests.get(url1)
    if response1.status_code != 200:
        await ctx.send('Ошибка загрузки изображения')
        return
    embed = discord.Embed(color=0x000000)
    embed.set_image(url=url1)
    await ctx.author.send(embed=embed)
    black_embed = discord.Embed(color=0x000000, description="20-9-23-5")
    await ctx.author.send(embed=black_embed)
  
@kgb.command(description = "Создаёт фейковый ютуб комментарий")
@helpCategory('fun')
async def comment(ctx, *, commint):
    if isinstance(ctx.channel, discord.DMChannel):
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
                await ctx.send(embed=discord.Embed(
                  title="Ваш коммент:",
                  description="",
                  color=discord.Color(0x000000)
                ).set_image(url="attachment://youtube_comment.gif"), file=discord.File(imageData, 'youtube_comment.gif'))
              
@kgb.command(description = "Список благодарностей")
@helpCategory('misc')
async def thank(ctx):
  if isinstance(ctx.channel, discord.DMChannel):
    return
  await ctx.send(embed = discord.Embed(
    title = "Я благодарен:",
    description = "SvZ_Bonnie#5779, за предоставленный обучающий материал!\nGrisshink#6476, за помощь в создании системы предупреждений!\nSanechka#1384 за рисование аватара для бота и постоянную поддержку меня:3",
    color = discord.Color(0xffff00)
  ))
  
@kgb.command(description = "Даёт информацию о сервере")
@helpCategory('info')
async def server(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
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
    embed = discord.Embed(title=f"Информация о сервере {guild.name}", color=0x000000)
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
    if isinstance(ctx.channel, discord.DMChannel):
        return
    guild_id = str(ctx.guild.id)
    if arg == "off":
        channels.pop(guild_id, None)
        with open("data/channels.json", "w") as f:
            json.dump(channels, f)
        await ctx.send(embed=discord.Embed(
            title="Приветствия выключены:",
            description="Теперь они больше не буду присылаться в этот канал.",
            color=discord.Color(0x000000)
        ))
    else:
        channel_id = str(ctx.channel.id)
        channels[guild_id] = channel_id
        with open("data/channels.json", "w") as f:
            json.dump(channels, f)
        await ctx.send(embed=discord.Embed(
            title="Приветствия включены:",
            description=f"Приветственные сообщения теперь буду присылаться в этот канал: \n{ctx.channel.mention}",
            color=discord.Color(0x000000)
        ))
  
@kgb.command(description = "Покажет аватар пользователя")
@helpCategory('info')
async def avatar(ctx, user: discord.User=None):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    server = ctx.author.guild
    if not user:
        user = ctx.message.author
    if server.get_member(user.id):
        user = server.get_member(user.id)
        userColor = user.colour
    else:
        userColor = 0x0000000
    embed=discord.Embed(title=f"Аватар {no_format(user)}", color=userColor)
    embed.set_image(url=user.avatar.url)
    await ctx.send(embed=embed)
  
@kgb.command(description = "Даёт информацию о пользователе")
@helpCategory('info')
async def user(ctx, member: discord.Member):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    status = str(member.status)
    tag = member.name + "#" + member.discriminator
    created_at = member.created_at.strftime("%d.%m.%Y %H:%M:%S")
    joined_at = member.joined_at.strftime("%d.%m.%Y %H:%M:%S")
    is_bot = "Это аккаунт бота" if member.bot else "Это аккаунт человека"
    is_admin = "Администратор сервера" if member.guild_permissions.administrator else "Это не администратор сервера"
    member_id = member.id
    avatar_url = member.avatar.url
    embed = discord.Embed(title="Информация о пользователе:", color=0x000000)
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
    if isinstance(ctx.channel, discord.DMChannel):
      return
    result = random.choice(["орёл", "решка"])
    await ctx.send(embed = discord.Embed(
          title = "Результат:",
          description = f"Монетка показывает: **{result}**!",
          color = discord.Color(0x000000)
        ))
  
@kgb.command(description = "Выдаст предупреждение пользователю")
@commands.has_permissions(administrator=True)
@helpCategory('moderation')
async def warn(ctx, member: discord.Member, count: int=1):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
  
    if member.top_role >= ctx.author.top_role:
      await ctx.send(embed=discord.Embed(
        title="Ошибка:",
        description="Вы не можете выдать пользователю предупредение с большей или равной ролью, чем у вас.",
        color=discord.Color(0xFF0000)
     ))

    if user_id == '1061907927880974406':
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description="Нет, сэр",
          color=discord.Color(0xFF0000)
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
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description='Условия кика и/или бана не настроены.\nУстановите их с помощью команды:\n`kgb!configwarn`',
          color=discord.Color(0xFF0000)
        ))
        return

    guild_stanwarns = stanwarns[guild_id]
    
    warn_type = guild_stanwarns.get('warn_type')
    warn_limit = guild_stanwarns.get('warn_limit')

    if total_warns >= warn_limit:
        if warn_type == 'kick':
            await member.kick()
            await ctx.send(embed = discord.Embed(
          title = "Кик:",
          description = f'{member.name} былъ кикнут. \nДостигнутъ лимит предупреждений: {total_warns}/{warn_limit}',
          color = discord.Color(0x000000)
        ))
            return

        if warn_type == 'ban':
            await member.ban(reason=f'Достигнут лимит предупреждений: {total_warns}/{warn_limit}')
            await ctx.send(embed = discord.Embed(
              title = "Бан:",
              description = f'{member.name} былъ забанен. \nДостигнут лимит предупреждений: {total_warns}/{warn_limit}',
              color = discord.Color(0x000000)
            ))

            del warns[guild_id][user_id]
            with open('data/warn.json', 'w') as f: 
                json.dump(warns, f)
            return

        await ctx.send(embed=discord.Embed(
          title="Конуз:",
          description=f'Невозможно произвести кик или бан {member.name}, т.к. указан неверный тип в configwarn',
          color=discord.Color(0xFF0000)
        ))

    with open('data/warn.json', 'w') as f: 
        json.dump(warns, f)

    await ctx.send(embed = discord.Embed(
              title = "Выдано предупреждение:",
              description = f'{member.mention} получил {count} предупреждение,\nТеперь он имеет {total_warns} предупреждений на этом сервере.',
              color = discord.Color(0x000000)
            ))

@kgb.command(description = "Снимет предупреждение пользователя")
@commands.has_permissions(administrator=True)
@helpCategory('moderation')
async def unwarn(ctx, member: discord.Member, count: int = 1):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    guild = str(ctx.guild.id)
    user = str(member.id)
  
    if user == '1061907927880974406':
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description="Нет, сэр",
          color=discord.Color(0xFF0000)
        ))
        return
      
    with open('data/stanwarns.json', 'r') as f:
        stanwarns = json.load(f)

    if guild not in stanwarns:
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description='Не установлены условия для предупреждений\nУстановите с помощью команды:\n`kgb!configwarn`',
          color=discord.Color(0xFF0000)
        ))
        return

    with open('data/warn.json', 'r') as f:
        warns = json.load(f)

    if guild not in warns:
        await ctx.send(embed=discord.Embed(
          title="Нет предупреждений:",
          description=f'У {member.mention} нет предупреждений на этом сервере.',
          color=discord.Color(0x000000)
        ))
        return

    if user not in warns[guild]:
        await ctx.send(embed=discord.Embed(
          title="Нет предупреждений:",
          description=f'У {member.mention} нет предупреждений на этом сервер.',
          color=discord.Color(0x000000)
        ))
        return

    if count > warns[guild][user]:
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description=f'У {member.mention} всего {warns[user][str(guild)]} предупреждений на этом сервере, вы не можете снять больше чем у него есть.',
          color=discord.Color(0xFF0000)
        ))
        return

    warns[guild][user] -= count
    total_warns = warns[guild][user]

    with open('data/warn.json', 'w') as f:
        json.dump(warns, f)

    await ctx.send(embed = discord.Embed(
              title = "Снято предупреждени(е/и):",
              description = f'{count} предупреждений успешно снято у {member.mention}. \nОсталось {total_warns} предупреждени(й/я/е) на этом сервере.',
              color = discord.Color(0x000000)
            ))

@kgb.command(description = "Покажет сколько предупреждений у пользователя")
@commands.has_permissions(administrator=True)
@helpCategory('moderation')
async def warnings(ctx, member: discord.Member):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    guild = str(ctx.guild.id)
    user = str(member.id)
    
    if user == '1061907927880974406':
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description="Нет, сэр",
          color=discord.Color(0xFF0000)
        ))
        return

    with open('data/warn.json', 'r') as f:
        warns = json.load(f)
    
    with open('data/stanwarns.json', 'r') as f:
        stanwarns = json.load(f)

    if guild not in stanwarns:
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description='Не установлены условия для предупреждений\nУстановите с помощью команды:\n`kgb!configwarn`',
          color=discord.Color(0xFF0000)
        ))
        return

    if guild not in warns:
        await ctx.send(embed = discord.Embed(
              title = "Ошибка:",
              description = 'На этом сервере не выдавалось никаких предупреждений',
              color = discord.Color(0x000000)
            ))
        return

    if user not in warns[guild]:
        await ctx.send(embed = discord.Embed(
              title = "Ошибка:",
              description = f'{member.display_name} не имеет предупреждений на этом сервере.',
              color = discord.Color(0x000000)
            ))
        return

    total_warns = warns[guild][user]
    await ctx.send(embed = discord.Embed(
              title = "Всего предупреждений:",
              description = f'{member.display_name} имеет {total_warns} предупреждений на этом сервере.',
              color = discord.Color(0x000000)
            ))

@kgb.command(description = "Установит лимит предупреждений и действия после него")
@commands.has_permissions(administrator=True)
@helpCategory('config')
async def configwarn(ctx, limit: int, warn_type: str):
    if isinstance(ctx.channel, discord.DMChannel):
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
        await ctx.send(embed=discord.Embed(
          title="Ошибка:",
          description='Неверный тип предупреждения. Доступны "kick" и "ban".',
          color=discord.Color(0xFF0000)
        ))
        return

    with open('data/stanwarns.json', 'w') as f:
        json.dump(stanwarns, f)

    await ctx.send(embed = discord.Embed(
              title = "Действие и лимит установлен:",
              description = f'Для сервера {ctx.guild.name} установлено {warn_type} при {limit} предупреждениях.',
              color = discord.Color(0x000000)
            ))

@kgb.command(description="Пригласить бота и другие полезные ссылки")
@helpCategory('misc')
async def invite(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    embed=discord.Embed(
      title=f"Пригласить {kgb.user.name}", 
      description=f"[Добавить {kgb.user.name}](https://discord.com/api/oauth2/authorize?client_id={kgb.user.id}&permissions=8&scope=bot) на свой сервер\n[Присоединится](https://discord.gg/CDMaFC84JE) к серверу бота", 
      color=discord.Color(0x000000))
    embed.set_footer(text=f"{kgb.user.name} находится на {len(kgb.guilds)} серверах")
    await ctx.send(embed=embed)

@kgb.command(description="Ищет пользователей по их примерному нику на всех серверах, где присутствует бот")
@helpCategory('info')
async def seek_user(ctx, *, query):
    if isinstance(ctx.channel, discord.DMChannel):
        return
    users_found = set()
    for guild in kgb.guilds:
        for member in guild.members:
            if query.lower() in member.display_name.lower() or query.lower() in member.name.lower():
                users_found.add(f"{member.name}")

    if not users_found:
        await ctx.send(embed=discord.Embed(
            title="Ошибка:",
            description=f"Не могу найти пользователя по запросу '{query}'",
            color=discord.Color(0xFF0000)
        ))
    else:
        message = "\n".join(users_found)
        users_count = f"Найдено пользователей: {len(users_found)}"
        await ctx.send(embed=discord.Embed(
            title="Найденные пользователи:",
            description=f"{message}\n\n{users_count}",
            color=discord.Color(0x000000)
        ))

@kgb.command(description="Ищет сервер, на котором находится пользователь по его точному нику, на всех серверах где присутствует бот ")
@helpCategory('info')
async def seek_server(ctx, *, user_name):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    guild_seek = None
    with open(GUILD_SEEK_FILENAME, "r", encoding="utf-8") as f:
        guild_seek = json.load(f)

    found_servers = []
    count = 0  # добавляем переменную для подсчета найденных серверов
    for guild_id, guild_info in guild_seek.items():
        for user in guild_info['users']:
            if user_name.lower() == f"{user['name']}".lower():
                guild = kgb.get_guild(int(guild_id))
                found_servers.append(guild.name)
                count += 1  # увеличиваем переменную на 1 при каждом найденном сервере

    if not found_servers:
        await ctx.send(embed=discord.Embed(
            title="Ошибка:",
            description=f"Не могу найти сервер, на котором находится пользователь {user_name}",
            color=discord.Color(0xFF0000)
        ))
    else:
        message = "\n".join(found_servers)
        message_count = f"Всего найдено серверов: {count}"
        await ctx.send(embed=discord.Embed(
            title="Вот сервера на которых есть пользователь:",
            description=f"{message}\n\n{message_count}",
            color=discord.Color(0x000000)
        ))
      
@kgb.command(description = "Покажет пинг бота")
@helpCategory('misc')
async def ping(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    latency = kgb.latency
    await ctx.send(embed=discord.Embed(
            title="Понг!",
            description=f'Скорость: {latency*1000:.2f} мс',
            color=discord.Color(0x000000)
        ))

@kgb.command(description="Выведет рандомное число")
@helpCategory('fun')
async def rand(ctx, num1, num2=None):
    if isinstance(ctx.channel, discord.DMChannel):
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
            await ctx.send(embed=discord.Embed(
            title="Результат:",
            description=result,
            color=discord.Color(0x000000)
        ))

@kgb.command(description='Переведёт кириллицу в транслит')
@helpCategory('fun')
async def tt(ctx, *, text):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    translit_text = unidecode.unidecode(text)
    await ctx.send(embed=discord.Embed(
            title="Перевод на транслит:",
            description=translit_text,
            color=discord.Color(0x000000)
        ))

@kgb.command(description='Переведёт транслитъ в кириллицу')
@helpCategory('fun')
async def tc(ctx, *, text: str):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    cyrillic_text = text.translate(translit_table)
    await ctx.send(embed=discord.Embed(
            title="Перевод на кирилицу",
            description=cyrillic_text,
            color=discord.Color(0x000000)
        ))

@kgb.command(description='Ищет статью на вики')
@helpCategory('fun')
async def wiki(ctx, *, query):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    wikipedia.set_lang('ru')
    try:
        page = wikipedia.page(query)
        await ctx.send(embed=discord.Embed(
            title="Найдена страница",
            description=page.url,
            color=discord.Color(0x000000)
        ))
    except wikipedia.exceptions.PageError:
        await ctx.send(embed=discord.Embed(
            title="Ошибка:",
            description=f'Страница на Википедии не найдена для "{query}"',
            color=discord.Color(0xFF0000)
        ))
    except wikipedia.exceptions.DisambiguationError as e:
        await ctx.send(embed=discord.Embed(
            title="Ошибка:",
            description=f'Слишком много результатов для "{query}". Пожалуйста, уточните свой запрос.',
            color=discord.Color(0xFF0000)
        ))

@kgb.command(description = ")")
async def hentai(ctx):
  if isinstance(ctx.channel, discord.DMChannel):
    return
  await ctx.send(embed = discord.Embed(
    title = "Не-а)",
    description = "Эй школьник, домашку сделай а потом дрочи)",
    color = discord.Color(0xff0000)
  ))

@kgb.command(description="Поцеловать участника")
@helpCategory('rp')
async def kiss(ctx, member: discord.Member):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    await ctx.send(f"{ctx.author.mention} поцеловал(а) {member.mention}")

@kgb.command(description="Обнять участника")
@helpCategory('rp')
async def hug(ctx, user: discord.Member):
    if isinstance(ctx.channel, discord.DMChannel):
        return

    response = requests.get("https://some-random-api.com/animu/hug")
    data = response.json()
    image_url = data["link"]

    embed = discord.Embed()
    embed.set_image(url=image_url)
    embed.description = f"{ctx.author.mention} обнял(a) {user.mention}"
    embed.color=0x000000 
    await ctx.send(embed=embed)

@kgb.command(description="Ударить участника")
@helpCategory('rp')
async def hit(ctx, user: discord.Member):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    await ctx.send(f"{ctx.author.mention} ударил(а) {user.mention}")

@kgb.command(description="Лизнуть участника")
@helpCategory('rp')
async def lick(ctx, user: discord.Member):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    await ctx.send(f"{ctx.author.mention} лизнул(а) {user.mention}")

@kgb.command(description="Погладить участника")
@helpCategory('rp')
async def pet(ctx, member: discord.Member):
    if isinstance(ctx.channel, discord.DMChannel):
        return

    response = requests.get("https://some-random-api.com/animu/pat")
    data = response.json()
    image_url = data["link"]

    embed = discord.Embed()
    embed.set_image(url=image_url)
    embed.description = f"{ctx.author.mention} погладил(а) {member.mention}"
    embed.color=0x000000
    await ctx.send(embed=embed)

@kgb.command(description="Поприветствовать участника")
@helpCategory('rp')
async def hi(ctx, member: discord.Member):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    await ctx.send(f'{ctx.author.mention} поприветствовал(а) {member.mention}')

@kgb.command(description='Вызывает голосование в канале\n(принимает длительность голосования только в часах)' )
@helpCategory('moderation')
async def poll(ctx, hours: int, *, text=None):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    if text is None:
        embedVar = discord.Embed(
          title='Ошибка:', 
          description='Пожалуйста, укажите текст!', 
          color=0xff0000
        )
        await ctx.reply(embed=embedVar, mention_author=False)
    
    end_time = datetime.utcnow() + timedelta(hours=hours)
    end_time_msk = end_time + timedelta(hours=3)
    end_time_str = end_time_msk.strftime('%H:%M:%S')
    
    embedVar = discord.Embed(
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
    embedVar = discord.Embed(
      title='Голосование завершено!', 
      description=f'{text}\n\n🔼 - Да ({yes_votes})\n🔽 - Нет ({no_votes})', 
      color=0x000000
    )
    await msgp.edit(embed=embedVar)

@kgb.command(description="Пишет информацию о категории\n(указывайте айди категории или её пинг")
@helpCategory('info')
async def category(ctx, category: discord.CategoryChannel):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    em = discord.Embed(title="Информация о категории:", color=0x000000)
    em.set_thumbnail(url=ctx.guild.icon.url)
    em.add_field(name="Имя:", value=category.name, inline=False)
    em.add_field(name="Создана:", value=category.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
    em.add_field(name="ID:", value=category.id, inline=False)
    em.add_field(name="Позиция:", value=category.position, inline=False)
    em.add_field(name="Количество каналов:", value=len(channels), inline=False)
    await ctx.send(embed=em)
  
@kgb.command(description="Пишет информацию о канале\n(указывайте айди канала или его пинг)")
@helpCategory('info')
async def channel(ctx, channel: typing.Optional[discord.TextChannel]):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    channel = channel or ctx.channel
    em = discord.Embed(title="Информация о канале:", color=0x000000)
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
async def role(ctx, *, role: discord.Role):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    em = discord.Embed(title="Информация о роли:", color=0x000000)
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
    if isinstance(ctx.channel, discord.DMChannel):
      return
    fortun = fortune.get_random_fortune('static_data/fortune')
    await ctx.send(f"```{fortun}```")

@kgb.command(description="Выдаст рандомную шутку про Штирлица")
@helpCategory('fun')
async def shtr(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    shtr = fortune.get_random_fortune('static_data/shtirlitz')
    await ctx.send(f"```{shtr}```")

@kgb.command(description="0x00000000")
async def null(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        return
    embed = discord.Embed(title="NULL OF PROJECT", color=0x00000000)
    embed.set_image(url='https://media.discordapp.net/attachments/1067069690066767924/1095385824247423120/SPOILER_image.png')
    await ctx.reply(embed=embed)

@kgb.command(description="Хорни карта")
@helpCategory('fun')
async def horny(ctx, member: discord.Member = None):
    if isinstance(ctx.channel, discord.DMChannel):
        return
    member = member or ctx.author
    async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            async with session.get(
            f'https://some-random-api.com/canvas/horny?avatar={member.avatar.url}') as af:
                if 300 > af.status >= 200:
                    fp = io.BytesIO(await af.read())
                    file = discord.File(fp, "horny.png")
                    em = discord.Embed(
                        color=0xFFC0CB,
                    )
                    em.set_image(url="attachment://horny.png")
                    await ctx.send(embed=em, file=file)
                else:
                    await ctx.send('No horny :(')
                await session.close()

@kgb.command(description="hello comrade!")
@helpCategory('fun')
async def comrade(ctx, member: discord.Member = None):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    member = member or ctx.author
    async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            async with session.get(
            f'https://some-random-api.com/canvas/overlay/comrade?avatar={member.avatar.url}') as af:
                if 300 > af.status >= 200:
                    fp = io.BytesIO(await af.read())
                    file = discord.File(fp, "comrade.png")
                    em = discord.Embed(
                      color=0xff0000,
                    )
                    em.set_image(url="attachment://comrade.png")
                    await ctx.send(embed=em, file=file)
                else:
                    await ctx.send('No horny :(')
                await session.close()

#@kgb.command(description='Чатбот')
#async def chatbot(ctx, *, message):
#    if isinstance(ctx.channel, discord.DMChannel):
#      return
#    response = requests.get('https://some-random-api.com/chatbot', params={
#        'message': message,
#        'key': 'wlkMplI6cPas78JtMwzKpwgO5EqNUw7fsXtpm2bmLE332cuHN3VZXIs17QdQ0pi1'
#    })
#    data = response.json()
#    response_message = data
#    await ctx.send(response_message)

@kgb.command(description="Взлом пентагона")
@helpCategory('fun')
async def hackp(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
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
    if isinstance(ctx.channel, discord.DMChannel):
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

        voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
    except:
        pass

    while voice_client.is_playing():
        await asyncio.sleep(1)
    await asyncio.sleep(5)
    await voice_client.disconnect()

@kgb.command(description="Может проигрывать музыку только с ютуба")
@helpCategory('music')
async def play(ctx, url):
    if isinstance(ctx.channel, discord.DMChannel):
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

        voice_client.play(discord.FFmpegPCMAudio(url2))
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
    if isinstance(ctx.channel, discord.DMChannel):
      return
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@kgb.command(description='Вышлет вам код дискорд бота "SudoBot"')
@helpCategory('misc')
async def code(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    file_path = 'static_data/sudocode.py'
    file = discord.File(file_path)
    await ctx.send(file=file)

@kgb.command(description='Гадает по имени')
@helpCategory('fun')
async def info(ctx, *, name):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    try:
        age = get_age(name)
        nationality, nationality_probability = get_nationality(name)
        gender, gender_probability = get_gender(name)

        response = f'Имя: {name}\n'
        if age:
            response += f'Возраст: {age}\n'
        if gender:
            response += f'Гендер: {gender} (Вероятность: {gender_probability})\n'
        if nationality:
            response += f'Национальность: {nationality} (Вероятность: {nationality_probability})'

        await ctx.send(embed = discord.Embed(
          title = "Информация об имени:",
          description = response,
          color = discord.Color(0x000000)
        ))
    
    except Exception as e:
        print(f'An error occurred: {e}')
        await ctx.send('Ошибка.')

@kgb.command(description='Введите эту команду в тот канал куда вы хотите получать новости.\nНапишите в качестве агрумента "Off" если хотите отписаться от новостей.')
@helpCategory('config')
async def sub(ctx, arg=None):
    if isinstance(ctx.channel, discord.DMChannel):
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
    if isinstance(ctx.channel, discord.DMChannel):
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

            embed = discord.Embed(title=f"Информация о пользователе {username}", color=discord.Color.orange())
            for key, value in user_info.items():
                embed.add_field(name=key, value=value, inline=False)

            embed.set_thumbnail(url=data['profile']['images']['90x90']) 

            embed.set_footer(text=f"ID: {data['id']}")  

            await ctx.send(embed=embed)
        else:
            await ctx.send("Пользователь не найден.")
    except requests.exceptions.RequestException as e:
        print("Error:", e)

@kgb.command()
@helpCategory('fun')
async def person(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return
    image_url = 'https://thispersondoesnotexist.com'
    response = requests.get(image_url)

    await ctx.send(file=discord.File(io.BytesIO(response.content), 'generated_image.jpg'))

@kgb.command()
async def nasa(ctx):
    url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key": "oEUDnRapyzulvTNbWimSBmFldgwMZt5ZZgU547Xf" 
    }
    response = requests.get(url, params=params)
    data = response.json()

    embed = discord.Embed(title=data['title'], description=data['explanation'], color=discord.Color.dark_blue())
    embed.set_image(url=data['url'])

    await ctx.send(embed=embed)

HELP_EMB = buildHelpEmbed()
HELP_CAT_EMB = buildCategoryEmbeds()
kgb.run(getenv('DISCORD_TOKEN', ''))
