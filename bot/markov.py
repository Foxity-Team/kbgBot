import random
import re

MRK_START = '__start'
MRK_END = '__end'
DEFAULT_CONFIG = {
    'read': False,
    'reply_on_mention': False,
    'remove_mentions': True,
}

class MarkovGen:
    def __init__(self, states: dict[str, list[str]] = {}, config = DEFAULT_CONFIG) -> None:
        self.stateTable: dict[str, set[str]] = {k: set(v) for k,v in states.items()}
        self.config = DEFAULT_CONFIG | config

    def addMessage(self, inpMsg: str) -> None:
        samples = [v.lower() for v in inpMsg.split() if v != MRK_START and v != MRK_END]
        
        if len(samples) == 0: return

        samples.insert(0, MRK_START)
        samples.append(MRK_END)

        for i, val in enumerate(samples):
            if i + 1 > len(samples) - 1: break
            
            if val not in self.stateTable:
                self.stateTable[val] = set()

            self.stateTable[val].add(samples[i + 1])

    def dumpState(self) -> dict[str, list[str]]:
        return {k: list(v) for k,v in self.stateTable.items()}

    def generate(self, startMsg: str='') -> str:
        if len(self.stateTable) == 0: raise ValueError('No messages recorded!')

        out = [ MRK_START ]
        out.extend(startMsg.split())
        
        while out[-1] != MRK_END:
            try:
                nextVals = self.stateTable[out[-1]]
            except KeyError as exc:
                raise ValueError(f'Невозможно сгенерировать предложение, начинающеяся на {out[-1]}!') from exc
            out.append(random.choice(list(nextVals)))

        outString = ''.join([str(token) + ' ' for token in out if token != MRK_START and token != MRK_END])
        if not outString.startswith('http'):
            if self.config['remove_mentions']:
                sub = re.sub('(<@&*[0-9]*>)', '', outString.capitalize())
                if sub.strip() == '':
                    return '*(Пустое сообщение)*'
                return sub 
            return outString.capitalize()

        if self.config['remove_mentions']:
            sub = re.sub('(<@&*[0-9]*>)', '', outString)
            return sub 

        return outString

if __name__ == '__main__':
    generator = MarkovGen()
    generator.addMessage('Дарова мусороиды прекрасные')
    generator.addMessage('Прекрасные сегодня цветы')
    generator.addMessage('Сегодня собаки прекрасные топчут цветы мои хорошие')

    for _ in range(10):
        print(generator.generate())
