import random

MRK_START = '__start'
MRK_END = '__end'

class MarkovGen:
    def __init__(self, states: dict[str, set[str]] = {}) -> None:
        self.stateTable: dict[str, set[str]] = states

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

    def generate(self) -> str:
        if len(self.stateTable) == 0: raise ValueError('No messages recorded!')

        out = [ MRK_START ]
        
        while out[-1] != MRK_END:
            nextVals = self.stateTable[out[-1]]
            out.append(random.choice(list(nextVals)))

        return ''.join([str(token) + ' ' for token in out if token != MRK_START and token != MRK_END]).capitalize()

if __name__ == '__main__':
    generator = MarkovGen()
    generator.addMessage('Дарова мусороиды прекрасные')
    generator.addMessage('Прекрасные сегодня цветы')
    generator.addMessage('Сегодня собаки прекрасные топчут цветы мои хорошие')

    for _ in range(10):
        print(generator.generate())
