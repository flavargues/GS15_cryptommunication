def bin_to_bytes(bits: list) -> bytes:
    number = int(''.join(bits), 2)
    text = number.to_bytes((number.bit_length()+7)//8, 'big')
    return text


def bin_to_str(bits: list) -> str:
    number = int(''.join(bits), 2)
    text = number.to_bytes((number.bit_length()+7)//8, 'big').decode()
    return text


def bin_to_dec(bits: list) -> int:
    return int(''.join(bits), 2)


def bin_to_hex(bits: list) -> str:
    return hex(bin_to_dec(bits))


def str_to_bin(text: str) -> list:
    bits = bin(int.from_bytes(text.encode(), 'big'))[2:]
    bits = bits.zfill(8*((len(bits)+7)//8))
    return [bit for bit in bits]


def bytes_to_bin(bytes: bytes, length: int = 8) -> list:
    bits = bin(int.from_bytes(bytes, 'big'))[2:]
    bits = bits.zfill(length*((len(bits)+(length-1))//length))
    return [bit for bit in bits]


def bytes_to_hex(bytes: bytes) -> str:
    return "0x"+bytes.hex()


def dec_to_bin(number: int, length: int) -> list:
    bits = bin(number)[2:].zfill(length)
    return [bit for bit in bits]
