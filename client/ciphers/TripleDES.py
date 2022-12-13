from DES import DES
from utils import convert

class TripleDES:
    def __init__(self, text: bytes, keys: list) -> None:
        if len(keys) != 3:
            exit("Please provide 3 keys")
        self.text = text
        self.keys = keys

    def encrypt(self):
        cipher_text = self.text
        for i in range(3):
            round_des = DES(text=cipher_text, key=self.keys[i])
            cipher_text = round_des.encrypt()
        return cipher_text

    def decrypt(self):
        self.keys.reverse()
        plain_text = self.text
        for i in range(3):
            round_des = DES(text=plain_text, key=self.keys[i])
            plain_text = round_des.decrypt()
        return plain_text


# if (__name__ == "__main__"):
#     text = b"etfdegud"
#     keys = [b"hsdbxhzs", b"islfjjze", b"hhsdnwoz"]

#     clear = TripleDES(text=text, keys=keys)
#     cipher_text = clear.encrypt()
#     print("Cipher Text : ", convert.bytes_to_hex(cipher_text))

#     encrypted = TripleDES(text=cipher_text, keys=keys)
#     plain_text = encrypted.decrypt()
#     print("Plain Text", convert.bytes_to_hex(plain_text))
