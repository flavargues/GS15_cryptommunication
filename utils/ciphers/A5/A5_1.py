class A5_1:
    class LSFR:
        def __init__(
            self, *args, length: int = 0, session_key: str = "", frame_counter: str = ""
        ) -> None:
            # Step 1 Initializing the LSFR
            self.xored_bits = set(*args) - {length - 1}
            self.register = [0] * length

            # Step 2 Clocking LSFR with session key
            for key_bit in session_key:
                self.register.insert(self(key_bit), 0)

            # Step 3 Clocking LSFR with frame counter
            for frame_bit in frame_counter:
                self.register.insert(self(frame_bit), 0)

        def shift(self) -> None:
            feedback = self.register[0]
            for bit_index in self.xored_bits:
                feedback = feedback ^ self.register[bit_index]
            self.register.pop(0)
            self.register.append(feedback)

        def __getitem__(self, item) -> int:
            return self.register[item]

        def __repr__(self) -> str:
            return str(self.register)

        def __call__(self, bit):
            feedback = self.register[-1]
            for bit_index in self.xored_bits:
                feedback = feedback ^ self.register[bit_index]
            return feedback ^ bit

    def __init__(self, key="") -> None:
        if not key != "":
            raise ValueError(f"Seed not defined={key}.")
        for digit in key:
            if digit not in ["0", "1"]:
                raise ValueError(f"Non binary digit in key={key}.")
        self.key = key

    def __call__(self, block, frame_counter):
        self.lsfrs = [
            self.LSFR(
                13,16,17,18,
                length=19,
                session_key=self.key,
                frame_counter=frame_counter,
            ),
            self.LSFR(
                20, 21, length=22, session_key=self.key, frame_counter=frame_counter
            ),
            self.LSFR(
                7,20,21,22,
                length=23,
                session_key=self.key,
                frame_counter=frame_counter,
            ),
        ]

        # Step 4 : Clocking LFSRs with majority vote
        for _ in range(0, 100 - 1):
            self.__shift()

        output = []
        for bit in block:
            random_bit = self.lsfrs[0][0] ^ self.lsfrs[1][0] ^ self.lsfrs[2][0]
            output.append(bit ^ random_bit)
            self.__shift()

        return output

    def __shift(self) -> None:
        clocking_bits = [self.lsfrs[0][8], self.lsfrs[1][10], self.lsfrs[2][10]]
        most_common = max(set(clocking_bits), key=clocking_bits.count)
        for lsfr in self.lsfrs:
            if lsfr[0] == most_common:
                lsfr.shift()
