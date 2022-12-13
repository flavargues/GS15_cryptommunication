import convert


def rotate_left(block: list['0' or '1'], shift_by: int)-> list['0' or '1']:
    result = []
    for index in range(len(block)):
        pos = (index+shift_by) % len(block)
        result.append(block[pos])
    return result


def shift_right(block: list['0' or '1'], shift_by: int) -> list['0' or '1']:
    result = shift_by*['0'] + block
    return result[:len(block)]


def rotate_right(block: list['0' or '1'], shift_by: int) -> list['0' or '1']:
    result = []
    for index in range(len(block)):
        pos = (index-shift_by) % len(block)
        result.append(block[pos])
    return result


def permute(block: list['0' or '1'], array: list[int], length: int) -> list['0' or '1']:
    return [
        block[array[i]-1]
        for i in range(length)
    ]


def xor(*blocks: list['0' or '1']) -> list['0' or '1']:
    result = blocks[0]
    for index in range(1, len(blocks)):
        block1 = result
        block2 = blocks[index]
        result = [
            '1' if (block1[i] != block2[i]) else '0'
            for i in range(len(block1))
        ]
    return result


def xand(*blocks: list['0' or '1']) -> list['0' or '1']:
    result = blocks[0]
    for index in range(1, len(blocks)):
        block1 = result
        block2 = blocks[index]
        result = [
            '1' if (block1[i] == block2[i] and block1[i] == '1') else '0'
            for i in range(len(block1))
        ]
    return result


def xnot(block1: list['0' or '1']) -> list['0' or '1']:
    return [
        '1' if (block1[i] == '0') else '0'
        for i in range(len(block1))
    ]


def add(*blocks: list['0' or '1'], length: int = 32) -> list['0' or '1']:
    result = convert.bin_to_dec(blocks[0])
    for index in range(1, len(blocks)):
        result += convert.bin_to_dec(blocks[index])

    return convert.dec_to_bin(result % 2**32, 32)
