from ....key import SymetricKey


class A5_1:
    # Tapped bits - {last bit that we don't xor with itself}
    T1 = {13, 16, 17, 18} - {18}
    T2 = {20, 21} - {21}
    T3 = {7, 20, 21, 22} - {22}

    def __init__(
        self, key: SymetricKey, frame_counter, direction, data
    ) -> None:
        self.key = key.bin_list()
        if len(frame_counter) != 22:
            raise ValueError("Frame frame_counterer length should be 22.")
        self.frame_counter = list(frame_counter)
        self.direction = direction # for duplex only
        self.data = data
        self.step1()


    def step1(self):
        # Initializing the LFSRs
        self.R1 = [0] * 19
        self.R2 = [0] * 22
        self.R3 = [0] * 23
        self.Rs = [self.R1, self.R2, self.R3]
        self.step2()

    def step2(self):
        # Clocking LFSRs with session key
        for keybit in self.key:
            self.__feed(keybit, keybit, keybit)
        self.step3()

    def step3(self):
        # Clocking LFSRs with frame counter
        for keybit in self.frame_counter:
            self.__feed(keybit, keybit, keybit)
        self.step4()

    def step4(self):
        # Clocking LFSRs with majority vote
        for _ in range(100):
            self.__irregular_clocking()
        self.step5()

    def step5(self):
        # Production of key stream
        self.key_stream = list()
        for _ in range(228):
            self.key_stream.append(self.__irregular_clocking())

    def step6(self):
        cipher_data = list()
        for key_stream, data_stream in zip(self.key_stream, self.data):
            cipher_data.append(key_stream ^ data_stream)

    def __clock(self):
        output1 = self.R1[-1]
        for tap in self.T1:
            output1 ^= self.R1[tap]
        output2 = self.R2[-1]
        for tap in self.T2:
            output2 ^= self.R2[tap]
        output3 = self.R3[-1]
        for tap in self.T3:
            output3 ^= self.R3[tap]
        return output1, output2, output3

    def __irregular_clocking(self):
        outputs = self.__clock()
        if outputs.count(0) >= 2:
            majority = 0
        else:
            majority = 1

        for index, bit in enumerate(outputs):
            if bit == majority:
                self.__shift(index, outputs[index])
        return outputs[0] ^ outputs[1] ^ outputs[2]

    def __shift(self, register_index, input):
        self.Rs[register_index].pop(0)
        self.Rs[register_index].append(input)

    def __feed(self, N1, N2, N3):
        self.R1.pop(0)
        self.R2.pop(0)
        self.R3.pop(0)
        self.R1.append(N1)
        self.R2.append(N2)
        self.R3.append(N3)