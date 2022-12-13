def bin_to_str(bits: list['0' or '1']) -> str:
    number = int(''.join(bits), 2)
    text = number.to_bytes((number.bit_length()+7)//8, 'big').decode()
    return text


def bin_to_hex(bits: list['0' or '1']) -> str:
    return hex(bin_to_dec(bits))


def bin_to_bytes(bits: list['0' or '1']) -> bytes:
    number = int(''.join(bits), 2)
    text = number.to_bytes((number.bit_length()+7)//8, 'big')
    return text


def bin_to_dec(bits: list['0' or '1']) -> int:
    return int(''.join(bits), 2)


def bytes_to_hex(bytes: bytes) -> str:
    return "0x"+bytes.hex()


def str_to_bin(text: str) -> list['0' or '1']:
    bits = bin(int.from_bytes(text.encode(), 'big'))[2:]
    bits = bits.zfill(8*((len(bits)+7)//8))
    return [bit for bit in bits]


def hex_to_bin(value: hex, length: int) -> list['0' or '1']:
    bits = bin(int(value))[2:].zfill(length)
    return [bit for bit in bits]


def bytes_to_bin(bytes: bytes, length: int = 8) -> list['0' or '1']:
    bits = bin(int.from_bytes(bytes, 'big'))[2:]
    bits = bits.zfill(length*((len(bits)+(length-1))//length))
    return [bit for bit in bits]


def dec_to_bin(number: int, length: int) -> list['0' or '1']:
    bits = bin(number)[2:].zfill(length)
    return [bit for bit in bits]
