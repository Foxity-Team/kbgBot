from typing import Callable
from discord import Embed, Colour
from functools import reduce

class KgbCategory:
    def __init__(self, name: str) -> None:
        self._name = name
        self._commands: set[str] = set()

    def getName(self) -> str: return self._name
    def getCommands(self) -> set[str]: return self._commands

    def addCommand(self, command: str) -> None:
        self._commands.add(command)

    def intoEmbed(self, embed: Embed) -> Embed:
        embed.add_field(name=self._name, value=reduce(lambda v,e: f'{v} `{e}`', self._commands, 'Команды:'), inline=False)
        return embed

    def getData(self) -> tuple[str, str]:
        return (self._name,
               reduce(lambda v,e: f'{v} `{e}`', self._commands, ''))

HELP_CATEGORIES = {
    'info'      : KgbCategory('📃 Просмотр информации'),
    'fun'       : KgbCategory('🎮 Развлечение'),
    'scratch'   : KgbCategory('😺 Скретч'),
    'music'     : KgbCategory('🎵 Музыка'),
    'rp'        : KgbCategory('🎭 РП'),
    'moderation': KgbCategory('🛡️ Модерация'),
    'config'    : KgbCategory('⚙️ Конфигурации'),
    'misc'      : KgbCategory('🛠 Остальное'),
}

def helpCategory(categoryName: str) -> Callable:
    def helpFunc(func: Callable) -> Callable:
        if categoryName not in HELP_CATEGORIES:
            raise ValueError(f'Category {categoryName} is not defined!')

        HELP_CATEGORIES[categoryName].addCommand(func.__name__)
        return func

    return helpFunc

def buildHelpEmbed() -> Embed:
    emb = Embed(title="Категории команд:", color=Colour(0x000000))

    for i, categ in enumerate(HELP_CATEGORIES.values()):
        catName, catVal = categ.getData()
        emb.add_field(name=f'{i+1}. {catName}', value=catVal, inline=False)

    emb.add_field(name="Что бы узнать команді из категории, напишите:", value="`kgb!help (цифра категории)`", inline=False)
    emb.set_thumbnail(url="https://media.discordapp.net/attachments/1068579157493153863/1094662619211780096/Bez_nazvania2_20230409092059.png")
    emb.set_footer(text="communist_fox", icon_url="https://media.discordapp.net/attachments/1068579157493153863/1094468823542943765/R44rlXiYjWw.jpg?width=425&height=425")
    
    return emb

def buildCategoryEmbeds() -> list[Embed]:
    embs = []
    for categ in HELP_CATEGORIES.values():
        emb = Embed(title=f"Категория: {categ.getName()}", color=Colour(0x000000))
        emb.add_field(name="Команды:", value=categ.getData()[1], inline=False)
        embs.append(emb)

    return embs

"""
        embed.add_field(name="1. 📃 Просмотр информации", value="Команды: `banlist` `server` `channel` `category` `role` `info` `warnings` `user` `avatar` `seek_user` `seek_server`", inline=False)
        embed.add_field(name="2. 🎮 Развлечение", value="Команды: `cat` `dog` `fox` `ball` `coin` `hack` `hackp` `comrade` `comment` `rand` `wiki` `tt` `tc` `quote` `shtr` `horny`", inline=False)
        embed.add_field(name="3. 😺 Скретч", value="Команды: `scratch_user`", inline=False)
        embed.add_field(name="4. 🎵 Музыка", value="Команды: `play` `playaudio` `leave`", inline=False)
        embed.add_field(name="5. 🎭 РП", value="Команды: `hug` `kiss` `hit` `lick` `hi` `pet`", inline=False)
        embed.add_field(name="6. 🛡️ Модерация", value="Команды: `ban` `unban` `kick` `clear` `warn` `unwarn` `poll`", inline=False)
        embed.add_field(name="7. ⚙️ Конфигурации", value="Команды: `configwarn` `welcome` `sub`", inline=False)
        embed.add_field(name="8. 🛠 Остальное", value="Команды: `invite` `ping` `verlist` `thank` `null` `cipher` `code`", inline=False)
        embed.add_field(name="Использование:", value="Для получения списка команд из категории, используйте `kgb!help (номер категории)`. Например: `kgb!help 1`", inline=False)
        embed.add_field(name="Для получения информации о конкретной команде, используйте `kgb!help (команда)`", value="Например: `kgb!help ban`", inline=False)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1068579157493153863/1094662619211780096/Bez_nazvania2_20230409092059.png")
        embed.set_footer(text="Neso Hiroshi#3080", icon_url="https://media.discordapp.net/attachments/1068579157493153863/1094468823542943765/R44rlXiYjWw.jpg?width=425&height=425")
        await ctx.send(embed=embed)
    elif query.isdigit():
        category_number = int(query)
        if category_number == 1:
            embed = discord.Embed(title="Категория: Просмотр информации", color=discord.Colour(0x000000))
            embed.add_field(name="Команды:", value="`banlist` `server` `channel` `category` `role` `info` `warnings` `user` `avatar` `seek_user` `seek_server`", inline=False)
            await ctx.send(embed=embed)
        elif category_number == 2:
            embed = discord.Embed(title="Категория: Развлечение", color=discord.Colour(0x000000))
            embed.add_field(name="Команды:", value="`cat` `dog` `fox` `ball` `coin` `hack` `hackp` `comrade` `comment` `rand` `wiki` `tt` `tc` `quote` `shtr` `horny`", inline=False)
            await ctx.send(embed=embed)
        # позже добавлю
        else:
            embed = discord.Embed(title="Ошибка:", description="Неверный номер категории.", color=discord.Colour(0xFF0000))
            await ctx.send(embed=embed)
    else:
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
"""
