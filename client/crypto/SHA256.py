# Conversions
def bin_to_bytes(bits: list) -> bytes:
    number = int(''.join(bits), 2)
    text = number.to_bytes((number.bit_length()+7)//8, 'big')
    return text


def bin_to_dec(bits: list) -> int:
    return int(''.join(bits), 2)


def hex_to_bin(value, length: int) -> list:
    bits = bin(int(value))[2:].zfill(length)
    return [bit for bit in bits]


def bytes_to_bin(bytes: bytes, length: int = 8) -> list:
    bits = bin(int.from_bytes(bytes, 'big'))[2:]
    bits = bits.zfill(length*((len(bits)+(length-1))//length))
    return [bit for bit in bits]


def dec_to_bin(number: int, length: int) -> list:
    bits = bin(number)[2:].zfill(length)
    return [bit for bit in bits]


# Operations
def shift_right(block: list, shift_by: int) -> list:
    result = shift_by*['0'] + block
    return result[:len(block)]


def rotate_right(block: list, shift_by: int) -> list:
    result = []
    for index in range(len(block)):
        pos = (index-shift_by) % len(block)
        result.append(block[pos])
    return result


def xor(*blocks: list) -> list:
    result = blocks[0]
    for index in range(1, len(blocks)):
        block1 = result
        block2 = blocks[index]
        result = [
            '1' if (block1[i] != block2[i]) else '0'
            for i in range(len(block1))
        ]
    return result


def xand(*blocks: list) -> list:
    result = blocks[0]
    for index in range(1, len(blocks)):
        block1 = result
        block2 = blocks[index]
        result = [
            '1' if (block1[i] == block2[i] and block1[i] == '1') else '0'
            for i in range(len(block1))
        ]
    return result


def xnot(block1: list) -> list:
    return [
        '1' if (block1[i] == '0') else '0'
        for i in range(len(block1))
    ]


def add(*blocks: list, length: int = 32) -> list:
    result = bin_to_dec(blocks[0])
    for index in range(1, len(blocks)):
        result += bin_to_dec(blocks[index])

    return dec_to_bin(result % 2**32, 32)


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


def get_word(message_schedule: list, index: int, length: int = 32):
    begin = index*length
    end = begin+length
    return message_schedule[begin:end]


def set_word(message_schedule: list, index: int, word_value: list, length: int = 32):
    begin = index*length
    end = begin+length
    return message_schedule[:begin] + word_value + message_schedule[end:]


def SHA256(text: bytes) -> bytes:
    # Preprocessing
    bin_text = bytes_to_bin(text)
    payload_length = len(text)+64+1
    message_block = bin_text + ['1']
    zeros = (512 - payload_length % 512)*['0']
    message_block += zeros + dec_to_bin(len(bin_text), 64)

    # Chunk loop
    hash_values = [
        hex_to_bin(HASH_CONSTANTS[i], 32) for i in range(len(HASH_CONSTANTS))
    ]
    for chunk_index in range(len(message_block)//512):
        begin = 512*chunk_index
        end = begin+512
        chunk = message_block[begin:end]

        # Create message schedule
        message_schedule = chunk + (48*32)*['0']
        for word_index in range(16, 64):
            w_i_15 = get_word(message_schedule, word_index-15)
            w_i_2 = get_word(message_schedule, word_index-2)
            w_i_16 = get_word(message_schedule, word_index-16)
            w_i_7 = get_word(message_schedule, word_index-7)
            s0 = xor(
                rotate_right(w_i_15, 7),
                rotate_right(w_i_15, 18),
                shift_right(w_i_15, 3)
            )
            s1 = xor(
                rotate_right(w_i_2, 17),
                rotate_right(w_i_2, 19),
                shift_right(w_i_2, 10)
            )
            word_value = add(w_i_16, s0, w_i_7, s1, length=32)

            message_schedule = set_word(
                message_schedule, word_index, word_value, 32)

        # Compression
        a, b, c, d, e, f, g, h = hash_values
        for round in range(64):
            s1 = xor(
                rotate_right(e, 6),
                rotate_right(e, 11),
                rotate_right(e, 25)
            )
            ch = xor(
                xand(e, f),
                xand(xnot(e), g)
            )
            temp1 = add(
                h, s1, ch,
                hex_to_bin(ROUND_CONSTANTS[round], 32),
                get_word(message_schedule, round)
            )
            s0 = xor(
                rotate_right(a, 2),
                rotate_right(a, 13),
                rotate_right(a, 22)
            )
            maj = xor(
                xand(a, b),
                xand(a, c),
                xand(b, c)
            )
            temp2 = add(s0, maj)
            h = g
            g = f
            f = e
            e = add(d, temp1)
            d = c
            c = b
            b = a
            a = add(temp1, temp2)

        working_variables = [a, b, c, d, e, f, g, h]

        # Modify final values
        hash_values = [
            add(hash_values[0], working_variables[0]),
            add(hash_values[1], working_variables[1]),
            add(hash_values[2], working_variables[2]),
            add(hash_values[3], working_variables[3]),
            add(hash_values[4], working_variables[4]),
            add(hash_values[5], working_variables[5]),
            add(hash_values[6], working_variables[6]),
            add(hash_values[7], working_variables[7]),
        ]

    # Concatenate final values and return the digest
    digest = []
    for i in range(8):
        digest += hash_values[i]
    return bin_to_bytes(digest)


# if (__name__ == "__main__"):
#     sha = SHA256(
#         b"azertyuiopqsdfghjklmwxcvbnazertyuiopqsdfghjklmwxcvbnazertyuiopqsdfghjklmwxcvbnazertyuiopqsdfghjklmwxcvbn")
#     print(sha)
#     pass
