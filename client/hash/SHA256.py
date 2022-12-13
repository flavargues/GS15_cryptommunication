from utils import convert
from utils import operation


HASH_CONSTANTS = (
    0x6a09e667,
    0xbb67ae85,
    0x3c6ef372,
    0xa54ff53a,
    0x510e527f,
    0x9b05688c,
    0x1f83d9ab,
    0x5be0cd19,
)
ROUND_CONSTANTS = (
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
)


class SHA256:
    def __init__(self, text: bytes):
        self.text: list = convert.bytes_to_bin(text)

    def pre_processing(self):
        payload_length = len(self.text)+64+1
        self.message_block = self.text + ['1']
        zeros = (512 - payload_length % 512)*['0']
        self.message_block += zeros + convert.dec_to_bin(len(self.text), 64)

    def chunk_loop(self):
        self.hash_values = [
            convert.hex_to_bin(HASH_CONSTANTS[i], 32) for i in range(len(HASH_CONSTANTS))
        ]
        for chunk_index in range(len(self.message_block)//512):
            print("chunk", chunk_index)
            begin = 512*chunk_index
            end = begin+512
            self.chunk = self.message_block[begin:end]
            self.create_message_schedule()
            self.compression()
            self.modify_final_values()

    def get_word(self, index: int, length: int = 32):
        begin = index*length
        end = begin+length
        return self.message_schedule[begin:end]

    def set_word(self, index: int, word_value: list, length: int = 32):
        begin = index*length
        end = begin+length
        self.message_schedule = self.message_schedule[:begin] + \
            word_value + self.message_schedule[end:]

    def create_message_schedule(self):
        self.message_schedule = self.chunk + (48*32)*['0']
        for word_index in range(16, 64):
            w_i_15 = self.get_word(word_index-15)
            w_i_2 = self.get_word(word_index-2)
            w_i_16 = self.get_word(word_index-16)
            w_i_7 = self.get_word(word_index-7)
            s0 = operation.xor(
                operation.rotate_right(w_i_15, 7),
                operation.rotate_right(w_i_15, 18),
                operation.shift_right(w_i_15, 3)
            )
            s1 = operation.xor(
                operation.rotate_right(w_i_2, 17),
                operation.rotate_right(w_i_2, 19),
                operation.shift_right(w_i_2, 10)
            )
            word_value = operation.add(w_i_16, s0, w_i_7, s1, length=32)

            self.set_word(word_index, word_value, 32)

    def compression(self):
        a, b, c, d, e, f, g, h = self.hash_values
        for round in range(64):
            s1 = operation.xor(
                operation.rotate_right(e, 6),
                operation.rotate_right(e, 11),
                operation.rotate_right(e, 25)
            )
            ch = operation.xor(
                operation.xand(e, f),
                operation.xand(operation.xnot(e), g)
            )
            temp1 = operation.add(
                h, s1, ch,
                convert.hex_to_bin(ROUND_CONSTANTS[round], 32),
                self.get_word(round)
            )
            s0 = operation.xor(
                operation.rotate_right(a, 2),
                operation.rotate_right(a, 13),
                operation.rotate_right(a, 22)
            )
            maj = operation.xor(
                operation.xand(a, b),
                operation.xand(a, c),
                operation.xand(b, c)
            )
            temp2 = operation.add(s0, maj)
            h = g
            g = f
            f = e
            e = operation.add(d, temp1)
            d = c
            c = b
            b = a
            a = operation.add(temp1, temp2)

        self.working_variables = [a, b, c, d, e, f, g, h]

    def modify_final_values(self):
        self.hash_values = [
            operation.add(self.hash_values[0], self.working_variables[0]),
            operation.add(self.hash_values[1], self.working_variables[1]),
            operation.add(self.hash_values[2], self.working_variables[2]),
            operation.add(self.hash_values[3], self.working_variables[3]),
            operation.add(self.hash_values[4], self.working_variables[4]),
            operation.add(self.hash_values[5], self.working_variables[5]),
            operation.add(self.hash_values[6], self.working_variables[6]),
            operation.add(self.hash_values[7], self.working_variables[7]),
        ]

    def concatenate_final_values(self):
        result = []
        for i in range(8):
            result += self.hash_values[i]
        self.hash_value = convert.bin_to_bytes(result)

    def hash(self):
        self.pre_processing()
        self.chunk_loop()
        self.concatenate_final_values()
        return self.hash_value


if (__name__ == "__main__"):
    sha = SHA256(
        b"azertyuiopqsdfghjklmwxcvbnazertyuiopqsdfghjklmwxcvbnazertyuiopqsdfghjklmwxcvbnazertyuiopqsdfghjklmwxcvbn").hash()
    print(sha)
    print(convert.bytes_to_hex(sha))
    pass
