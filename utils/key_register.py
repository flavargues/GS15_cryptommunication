from abc import ABC
from singleton import SingletonMeta

class Key(ABC):
    pass


class SymetricKey(Key):
    def __init__(self, key) -> None:
        if not key:
            raise ValueError('"key" can\'t be None.')
        self.key = key

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, SymetricKey):
            return self.key == __o.key
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return "SYM=" + str(self.key)

class AsymetricKey(Key):
    def __init__(self, pub_key, priv_key=None) -> None:
        if not pub_key:
            raise ValueError('"pub_key" can\'t be None.')
        self.pub_key = pub_key
        if priv_key and len(pub_key) != len(priv_key):
                raise ValueError("Different length between public and private key.")
        self.priv_key = priv_key

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, AsymetricKey):
            return self.priv_key == __o.priv_key and self.pub_key == __o.pub_key
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.pub_key)

    def __repr__(self) -> str:
        if self.priv_key:
            return "ASYM=" + str(self.pub_key) + "+" + str(self.priv_key)
        else:
            return "ASYM=" + str(self.pub_key)
            
class KeyRegister(metaclass=SingletonMeta):
    def __init__(self):
        self.register = set()

    def add(self, key):
        if isinstance(key, Key):
            return self.register.add(key)
        else:
            raise TypeError("Only Key subclasses")

    def discard(self, key):
        return self.register.discard(key)

    def remove(self, key):
        self.register.remove(key)

    def union(self, key):
        self.register.union(key)

    def update(self, key):
        self.register.update(key)
