import random
import sys
from discord import Message, Embed, Color, TextChannel
from discord.ext.commands import Bot

class Publisher:
    def __init__(self, publisher_chan_id: int, retr_filename: str) -> None:
        self.publish_id = publisher_chan_id
        self.retr_filename = retr_filename
        self.retr_data = self._readRetr()
        self.dirty = False

    def _readRetr(self) -> set[int]:
        try:
            with open(self.retr_filename, 'r') as f:
                return {int(chan_id) for chan_id in f}
        except FileNotFoundError:
            print(f'Файл {self.retr_filename} не найден. Создаём пустой файл...', file=sys.stderr)
            self.dirty = True
            return set()

    def sync_retr(self) -> None:
        if not self.dirty: return

        print(f'Синхронизация {self.publish_id}...', file=sys.stderr)
        with open(self.retr_filename, 'w') as f:
            for chid in self.retr_data:
                f.write(f'{chid}\n')
        self.dirty = False

    def subscribe(self, chan_id: int) -> bool:
        if chan_id in self.retr_data:
            return False

        self.retr_data.add(chan_id)
        self.dirty = True
        return True

    def unsubscribe(self, chan_id: int) -> bool:
        if chan_id not in self.retr_data:
            return False

        self.retr_data.remove(chan_id)
        self.dirty = True

        return True

    async def publish(self, bot: Bot, msg: Message) -> None:
        if msg.channel.id != self.publish_id: return
        if not isinstance(msg.channel, TextChannel): return

        embed_color = random.choice([0xFF0000, 0xFFFF00])
        embeds = [Embed(
            title=f'Сообщение из канала #{msg.channel.name}:',
            description=msg.content,
            color=Color(embed_color)
        )]
        if embeds[0].description == '': embeds.pop()

        sideAttachments = []
        for att in msg.attachments:
            if len(embeds) >= 10: break
            if not att.content_type: continue
            if att.content_type.split('/')[0] != 'image':
                sideAttachments.append(att)
                continue

            emb = Embed(
                title=f'Приложение {att.filename}',
                color=Color(embed_color),
            )
            emb.set_image(url=att.url)
            embeds.append(emb)

        files = [await att.to_file() for att in sideAttachments]

        blackChids = []
        for chid in self.retr_data:
            channel = bot.get_channel(chid)
            if not isinstance(channel, TextChannel):
                blackChids.append(chid)
                continue

            await channel.send(embeds=embeds, files=files)

        for id in blackChids: self.unsubscribe(id)
