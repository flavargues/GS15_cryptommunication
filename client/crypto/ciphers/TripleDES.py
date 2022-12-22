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
    def __init__(self, text: str, key: str) -> None:
        self.text: str = text
        self.key1: str = key[:64]
        self.key2: str = key[64:128]
        self.key3: str = key[128:192]

    def encrypt(self) -> str:
        cipher_text = self.text

        cipher_text = DES(cipher_text, self.key1).encrypt()
        cipher_text = DES(cipher_text, self.key2).decrypt()
        cipher_text = DES(cipher_text, self.key3).encrypt()

        return cipher_text

    def decrypt(self) -> str:
        plain_text = self.text

        plain_text = DES(plain_text, self.key3).decrypt()
        plain_text = DES(plain_text, self.key2).encrypt()
        plain_text = DES(plain_text, self.key1).decrypt()

        return plain_text


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
