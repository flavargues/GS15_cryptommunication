# class A5_1:
#     class LSFR:
#         def __init__(
#             self, *args, length: int = 0, session_key: str = "", frame_counter: str = ""
#         ) -> None:
#             # Step 1 Initializing the LSFR
#             self.xored_bits = set(*args) - {length - 1}
#             self.register = [0] * length

#             # Step 2 Clocking LSFR with session key
#             for key_bit in session_key:
#                 self.register.insert(self(key_bit), 0)

#             # Step 3 Clocking LSFR with frame counter
#             for frame_bit in frame_counter:
#                 self.register.insert(self(frame_bit), 0)

#         def shift(self) -> None:
#             feedback = self.register[0]
#             for bit_index in self.xored_bits:
#                 feedback = feedback ^ self.register[bit_index]
#             self.register.pop(0)
#             self.register.append(feedback)

#         def __getitem__(self, item) -> int:
#             return self.register[item]

#         def __repr__(self) -> str:
#             return str(self.register)

#         def __call__(self, bit):
#             feedback = self.register[-1]
#             for bit_index in self.xored_bits:
#                 feedback = feedback ^ self.register[bit_index]
#             return feedback ^ bit

#     def __init__(self, key="") -> None:
#         if not key != "":
#             raise ValueError(f"Seed not defined={key}.")
#         for digit in key:
#             if digit not in ["0", "1"]:
#                 raise ValueError(f"Non binary digit in key={key}.")
#         self.key = key

#     def __call__(self, block, frame_counter):
#         self.lsfrs = [
#             self.LSFR(
#                 13,
#                 16,
#                 17,
#                 18,
#                 length=19,
#                 session_key=self.key,
#                 frame_counter=frame_counter,
#             ),
#             self.LSFR(
#                 20, 21, length=22, session_key=self.key, frame_counter=frame_counter
#             ),
#             self.LSFR(
#                 7,
#                 20,
#                 21,
#                 22,
#                 length=23,
#                 session_key=self.key,
#                 frame_counter=frame_counter,
#             ),
#         ]

#         # Step 4 : Clocking LFSRs with majority vote
#         for _ in range(0, 100 - 1):
#             self.__shift()

#         output = []
#         for bit in block:
#             random_bit = self.lsfrs[0][0] ^ self.lsfrs[1][0] ^ self.lsfrs[2][0]
#             output.append(bit ^ random_bit)
#             self.__shift()

#         return output

#     def __shift(self) -> None:
#         clocking_bits = [self.lsfrs[0][8], self.lsfrs[1][10], self.lsfrs[2][10]]
#         most_common = max(set(clocking_bits), key=clocking_bits.count)
#         for lsfr in self.lsfrs:
#             if lsfr[0] == most_common:
#                 lsfr.shift()

from ....key import SymetricKey

class A5_1:
    #Tapped bits - {last bit that we don't xor with itself}
    T1 = {13,16,17,18} - {18}
    T2 = {20,21} - {21}
    T3 = {7,20,21,22} - {22}

    def __init__(self, key: SymetricKey, frame_counter, bearer, direction, data) -> None:
        self.key = key.bin_list()
        if len(frame_counter) != 22:
            raise ValueError("Frame frame_counterer length should be 22.")
        self.frame_counter = list(frame_counter)
        self.bearer = bearer
        self.direction = direction
        self.data = data
        

    def __clock(self):#-> int, int, int:
        output1 = self.R1[-1] ^ self.R1[x for x in self.T1]
        output2 = self.R2[-1] ^ self.R2[x for x in self.T2]
        output3 = self.R3[-1] ^ self.R3[x for x in self.T3]
        return output1, output2, output3

    def __irregular_clocking(self):
        ouputs = self.__clock()
        
        if ouputs.count(0) >= 2:
            majority = 0
        else:
            majority = 1
        
        for index, bit in enumerate(output, self.Rs):
            if bit == majority:
                self.__shift(index)
                



    def __shift(self, register) -> None:
        self.Rs[register].pop(0)

    def __feed(self, N1, N2, N3):
        self.R1.pop(0)
        self.R2.pop(0)
        self.R3.pop(0)
        self.R1.append(N1)
        self.R2.append(N2)
        self.R3.append(N3)


    def step1(self):
        #Initializing the LFSRs
        self.R1 = [0] * 19
        self.R2 = [0] * 22
        self.R3 = [0] * 23
        self.Rs = [self.R1, self.R2, self.R3]
        self.step2()

    def step2(self):
        # Clocking LFSRs with session key
        for keybit in self.key:
            self.__feed(keybit,keybit,keybit)
        self.step3()

    def step3(self):
        # Clocking LFSRs with frame counter
        for keybit in self.frame_counter:
            self.__feed(keybit,keybit,keybit)
        self.step4()

    def step4(self):
        # Clocking LFSRs with majority vote
        o1, o2, o3 = self.__clock()


        self.step5()
            
    def step5(self):
        pass
