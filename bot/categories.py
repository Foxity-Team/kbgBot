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
        catName, _ = categ.getData()
        emb.add_field(name=f'{i+1}. {catName}', value='', inline=False)

    emb.add_field(name="Что бы узнать команды из категории, напишите:", value="`kgb!help (цифра категории)`", inline=False)
    emb.set_thumbnail(url="https://media.discordapp.net/attachments/1068579157493153863/1094662619211780096/Bez_nazvania2_20230409092059.png")
    emb.set_footer(text="communist_fox", icon_url="https://media.discordapp.net/attachments/1068579157493153863/1094468823542943765/R44rlXiYjWw.jpg?width=425&height=425")
    
    return emb

def buildCategoryEmbeds() -> list[Embed]:
    embs = []
    for categ in HELP_CATEGORIES.values():
        emb = Embed(title=f"Категория: {categ.getName()}", color=Colour(0x000000))
        emb.add_field(name="Команды:", value=categ.getData()[1], inline=False)
        emb.add_field(name="Что бы узнать, что делает команда, напишите:", value="`kgb!help (команда)`", inline=False)
        emb.set_thumbnail(url="https://media.discordapp.net/attachments/1068579157493153863/1094662619211780096/Bez_nazvania2_20230409092059.png")
        emb.set_footer(text="communist_fox", icon_url="https://media.discordapp.net/attachments/1068579157493153863/1094468823542943765/R44rlXiYjWw.jpg?width=425&height=425")
        embs.append(emb)

    return embs
