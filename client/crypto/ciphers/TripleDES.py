from .DES import DES


def dec_to_bin(number: int, length: int) -> str:
    return bin(number)[2:].zfill(length)


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


class TripleDES:
    def __init__(self, block: str, key: str) -> None:
        self.block: str = block
        self.key1: str = key[:64]
        self.key2: str = key[64:128]
        self.key3: str = key[128:192]

    def encrypt(self) -> str:
        cipher_block = self.block

        cipher_block = DES(cipher_block, self.key1).encrypt()
        cipher_block = DES(cipher_block, self.key2).decrypt()
        cipher_block = DES(cipher_block, self.key3).encrypt()

        return cipher_block

    def decrypt(self) -> str:
        plain_block = self.block

        plain_block = DES(plain_block, self.key3).decrypt()
        plain_block = DES(plain_block, self.key2).encrypt()
        plain_block = DES(plain_block, self.key1).decrypt()

        return plain_block


# if (__name__ == "__main__"):
#     text = "bnbnh,j".encode()
#     text = dec_to_bin(int.from_bytes(text, byteorder='big'), 64)
#     key = b"hsdbxhzsislfjjzehhsdnwoz"
#     keys = dec_to_bin(int.from_bytes(key, byteorder='big'), 64)

#     print("Plain Text : ", hex(int(text, 2)))

#     clear = TripleDES(text, keys)
#     cipher_text = clear.encrypt()
#     print("Cipher Text : ", hex(int(cipher_text, 2)))

#     encrypted = TripleDES(cipher_text, keys)
#     plain_text = encrypted.decrypt()
#     print("Plain Text : ", hex(int(plain_text, 2)))
