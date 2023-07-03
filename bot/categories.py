from typing import Callable
from discord import Embed, Colour
from functools import reduce
from config import *

class KgbCategory:
    def __init__(self, name: str, hidden=False) -> None:
        self._name = name
        self._hidden = hidden
        self._commands: set[str] = set()

    def getName(self) -> str: return self._name
    def getCommands(self) -> set[str]: return self._commands
    def isHidden(self) -> bool: return self._hidden

    def addCommand(self, command: str) -> None:
        self._commands.add(command)

    def intoEmbed(self, embed: Embed) -> Embed:
        embed.add_field(name=self._name, value=reduce(lambda v,e: f'{v} `{e}`', self._commands, 'Команды:'), inline=False)
        return embed

    def getData(self) -> tuple[str, str]:
        outCommands = ''
        for i, val in enumerate(sorted(self._commands)):
            if (i+1) % 5 == 0:
                outCommands = f'{outCommands} `{val}`\n'
            else:
                outCommands = f'{outCommands} `{val}`'

        return self._name, outCommands

HELP_CATEGORIES = {
    'info'      : KgbCategory('📃 Просмотр информации'),
    'fun'       : KgbCategory('🎮 Развлечение'),
    'neuro'     : KgbCategory('🖥️ Нейросети'),
    'api'       : KgbCategory('🔑 Апи команды'),
    'scratch'   : KgbCategory('😺 Скретч'),
    'music'     : KgbCategory('🎵 Музыка'),
    'rp'        : KgbCategory('🎭 РП'),
    'secret'    : KgbCategory('☢️ Secret', hidden=True),
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

    for i, categ in enumerate(filter(lambda v: not v.isHidden(),HELP_CATEGORIES.values())):
        catName, _ = categ.getData()
        emb.add_field(name=f'{i+1} - {catName}', value='', inline=False)

    emb.add_field(name="Что бы узнать команды из категории, \nНапишите:", value="`kgb!help (цифра категории)`", inline=False)
    emb.add_field(name="Поддержать бота на бусти можно тут:", value=f"[Ваша поддержка очень важна для нас!]({boostyURL})", inline=False)
    emb.set_thumbnail(url=tumbaYUMBA)
    emb.set_footer(text="Soviet WorkShop © 2023", icon_url=avaURL)
    
    return emb

def buildCategoryEmbeds() -> tuple[list[Embed], dict[str, Embed]]:
    def addEmbed(categ: KgbCategory) -> Embed:
        emb = Embed(title=f"Категория: {categ.getName()}", color=Colour(0x000000))
        emb.add_field(name="Команды:", value=categ.getData()[1], inline=False)
        emb.add_field(name="Что бы узнать, что делает команда, \nНапишите:", value="`kgb!help (команда)`", inline=False)
        emb.set_thumbnail(url=tumbaYUMBA)
        emb.set_footer(text="Soviet WorkShop © 2023", icon_url=avaURL)
        return emb

    embs = [addEmbed(categ) for categ in filter(lambda v: not v.isHidden(), HELP_CATEGORIES.values())]
    embsHidden = {val: addEmbed(categ) for val, categ in HELP_CATEGORIES.items()}

    return embs, embsHidden
