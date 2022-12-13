# import logging
# logger = logging.getLogger(__name__)
from math import log2, ceil
import secrets
import numpy as np
import constants

class CipherKey:
    def __init__(self, mode) -> None:
        if mode not in constants.cipher_specs.keys():
            raise ValueError()
        self.mode = mode
        self.specs = constants.cipher_specs.get(mode)
        self.value = secrets.token_bytes(self.key_length)

    def __len__(self):
        return len(self.value)
        
    @property
    def key_length(self):
        return self.specs["key_length"]

    @property
    def key_word_length(self):
        return self.specs["key_word_length"]

    @property
    def block_size(self):
        return self.specs["block_size"]

    @property
    def number_rounds(self):
        return self.specs["number_rounds"]

        
    # class CipherKeyInvalid(Exception):
    #     pass


class AES:
    def __init__(self, key: CipherKey, decrypt: bool = False) -> None:
        if key.mode not in ["AES-128","AES-192","AES-256"]:
            raise ValueError()
        self.__decrypting: bool = decrypt
        self.__key: CipherKey = key
        self.__round_keys = list()

        self.__rounds = list()
        if self.__decrypting:
            __round = [
                self.__invAddRoundKey,
                self.__invMixColumns,
                self.__invSubBytes,
                self.__invShiftRows,
            ]
            self.__rounds.append(self.__invAddRoundKey)
            self.__rounds.append(self.__invShiftRows)
            self.__rounds.append(self.__invSubBytes)
            self.__rounds.extend(
                __round * self.__specs[self.__key.mode]["number_rounds"]
            )
            self.__rounds.append(self.__invAddRoundKey)
            self.__handling_func = self.__decrypt

        else:
            __round = [
                self.__subBytes,
                self.__shiftRows,
                self.__mixColumns,
                self.__addRoundKey,
            ]
            self.__rounds.append(self.__addRoundKey)
            self.__rounds.extend(
                __round * self.__specs[self.__key.mode]["number_rounds"]
            )
            self.__rounds.append(self.__subBytes)
            self.__rounds.append(self.__shiftRows)
            self.__rounds.append(self.__addRoundKey)
            self.__handling_func = self.__encrypt

    def __enter__(self):
        return self

    def __exit__(self):
        pass

    def __call__(self, data: bytes) -> bytes:
        padding = 16 - (len(data) % 16)
        data += b"0" * padding
        return_data = b""

        for x in range(0, len(data), 16):
            sixteen_bytes = data[x : x + 16]
            block = np.array(
                [
                    sixteen_bytes[0:3],
                    sixteen_bytes[4, 7],
                    sixteen_bytes[8, 11],
                    sixteen_bytes[12:15],
                ]
            )
            return_data += self.__handling_func(block)

        return return_data

    def __encrypt(self):
        pass

    def __decrypt(self):
        pass

    def __addRoundKey(self):
        pass

    def __invAddRoundKey(self, *args, **kwargs):
        return self.__addRoundKey(args, kwargs)

    def __subBytes(self):
        pass

    def __invSubBytes(self):
        pass

    def __shiftRows(self):
        pass

    def __invShiftRows(self):
        pass

    def __mixColumns(self):
        pass

    def __invMixColumns(self):
        pass

class KeyExpander:
    
    def __init__(self, key: CipherKey) -> None:
        self.key = key
        self.round_keys = list()
        self.blocks = [ key.value[x:x+3] for x in range(0, len(self.key), 4) ]

    def __rotWord(self, block: bytearray) -> bytearray:
        return block.append(block.pop(0))

    def __subWord(self, block: bytearray) -> bytearray:
        return bytearray([constants.Sbox[int(x)] for x in block])

    def __RCon(self, block: bytearray, i:int) -> bytearray:
        if i == 1:
            

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.round_keys) > self.key.n_rounds:
            raise StopIteration
        else:
            x = len(self.round_keys)
            self.blocks[x+3] = self.__rotWord(self.blocks[x+3])
            self.blocks[x+3] = self.__subWord(self.blocks[x+3])
            self.blocks[x+3] = self.__RCon(self.blocks[x+3])

            self.blocks[x+0:] ^= self.blocks[x+3:]
            self.blocks[x+1:] ^= self.blocks[x+0:]
            self.blocks[x+2:] ^= self.blocks[x+1:]

            key = self.blocks[x+0] + self.blocks[x+1] + self.blocks[x+2] + self.blocks[x+3]
            return key
