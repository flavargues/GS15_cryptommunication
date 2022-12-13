import convert
import operation


class LSFR:
    def __init__(self, seed: bytes, positions: list[int]):
        self.seed = convert.bytes_to_bin(seed)
        self.size = len(self.seed)
        self.positions = positions

    def generate(self):
        xor = '0'
        while True:
            for pos in self.positions:
                xor = '1' if (xor != self.seed[pos]) else '0'

    def iterate(self):
        self.state = self.seed
        for pos in self.positions:
            result = operation.rotate_right(self.state, pos)
            self.state = operation.xor(self.state, result)


def main():
    pass
