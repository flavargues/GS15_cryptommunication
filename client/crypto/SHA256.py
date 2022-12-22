def hex_to_bin(value, length: int) -> str:
    bits = bin(int(value))[2:].zfill(length)
    return bits


def bytes_to_bin(bytes: bytes, length: int = 8) -> list:
    bits = bin(int.from_bytes(bytes, 'big'))[2:]
    bits = bits.zfill(length*((len(bits)+(length-1))//length))
    return [bit for bit in bits]


def dec_to_bin(number: int, length: int) -> str:
    return bin(number)[2:].zfill(length)


# Operations
def shift_right(block: str, shift_by: int) -> str:
    result = shift_by*'0' + block
    return result[:len(block)]


def rotate_right(block: str, shift_by: int) -> str:
    result = ''
    for index in range(len(block)):
        pos = (index-shift_by) % len(block)
        result += block[pos]
    return result


def xor(*blocks) -> str:
    result = blocks[0]
    for b_index in range(1, len(blocks)):
        xand_result = ''
        block1 = result
        block2 = blocks[b_index]
        for i in range(len(block1)):
            xand_result += '1' if (block1[i] != block2[i]) else '0'
        result = xand_result
    return result


def xand(*blocks) -> str:
    result = blocks[0]
    for b_index in range(1, len(blocks)):
        xand_blocks = ''
        block1 = result
        block2 = blocks[b_index]
        for i in range(len(block1)):
            xand_blocks += '1' if (block1[i] == block2[i]
                                   and block1[i] == '1') else '0'
        result = xand_blocks
    return result


def xnot(block1: str) -> str:
    result = ''
    for i in range(len(block1)):
        result += '1' if (block1[i] == '0') else '0'
    return result


def add(*blocks: str, length: int = 32) -> str:
    result = int(blocks[0], 2)
    for index in range(1, len(blocks)):
        result += int(blocks[index], 2)

    return dec_to_bin(result % 2**length, length)


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


def get_word(message_schedule: str, index: int, length: int = 32):
    begin = index*length
    end = begin+length
    return message_schedule[begin:end]


def set_word(message_schedule: str, index: int, word_value: str, length: int = 32):
    begin = index*length
    end = begin+length
    return message_schedule[:begin] + word_value + message_schedule[end:]


def SHA256(text: int) -> int:
    # Preprocessing
    text_length = (text.bit_length()+7)//8*8
    bin_text = dec_to_bin(
        text, text_length
    )

    payload_length: int = len(bin_text)+64+1
    message_block: str = bin_text + '1'
    zeros: str = (512 - payload_length % 512)*'0'
    message_block += zeros + dec_to_bin(len(bin_text), 64)

    # Chunk loop
    hash_values = [
        hex_to_bin(HASH_CONSTANTS[i], 32) for i in range(len(HASH_CONSTANTS))
    ]

    for chunk_index in range(len(message_block)//512):
        begin: int = 512*chunk_index
        end: int = begin+512
        chunk: str = message_block[begin:end]

        # Create message schedule
        message_schedule: str = chunk + (48*32)*'0'
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

        # Modify final values
        hash_values = [
            add(hash_values[0], a),
            add(hash_values[1], b),
            add(hash_values[2], c),
            add(hash_values[3], d),
            add(hash_values[4], e),
            add(hash_values[5], f),
            add(hash_values[6], g),
            add(hash_values[7], h),
        ]

    # Concatenate final values and return the digest
    digest = ""
    for i in range(8):
        digest += hash_values[i]
    return int(digest, 2)


# if (__name__ == "__main__"):
#     text = "ghdjeksljhwdejskjflk,czenklsqfsmkekdfn,nedffc,nqkf,clmzea,nkhfkzelmnjfcbezkjlflkcnzel   jkznflnc".encode()
#     int_text = int.from_bytes(text, byteorder='big')
#     sha = SHA256(int_text)
#     print(hex(sha))
#     pass
