class LSFR:
    def __init__(self, length, *args, seed="", manual_shift=False) -> None:
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

        self.manual_shift = manual_shift

    def __call__(self, *args, **kwds):
        feedback = self.register[0]
        for bit_index in self.xored_bits:
            feedback = feedback ^ self.register[bit_index]

        if self.manual_shift:
            self.temp = feedback
            return self.register[0]
        else:
            self.register.append(feedback)
            return self.register.pop(0)

    def __repr__(self) -> str:
        return str(self.register)

    def shift(self):
        if not self.manual_shift:
            raise ArithmeticError(f"Request manual shift on auto LSFR.")
        else:
            self.register.pop(0)
            self.register.append(self.temp)
