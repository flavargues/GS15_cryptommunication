class LSFR:
    def __init__(self, length=0, seed="", *args) -> None:
        if not length > 0:
            raise ValueError(f"Length too small {length}<0.")
        self.length = length

        if not seed != "":
            raise ValueError(f"Seed not defined={seed}.")
        self.register = list()
        for digit in seed:
            if digit not in ["0", "1"]:
                raise ValueError(f"Non binary digit in seed={seed}.")
            self.register.append(int(digit))

        if not args:
            raise ValueError(f"No xored_bits defined={args}.")
        self.xored_bits = set()
        for xored_bit in args:
            if xored_bit > length:
                raise ValueError(f"Out of index xored bit index = {args}")
            self.xored_bits.add(xored_bit)

    def __call__(self, *args, **kwds):
        return self.__shift()

    def __shift(self):
        feedback = self.register[0]
        for bit_index in self.xored_bits:
            feedback = feedback ^ self.register[bit_index]
        self.register.append(feedback)
        return self.register.pop(0)

    def __repr__(self) -> str:
        return str(self.register)
