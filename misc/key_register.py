class Key:
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
        return self.key

class AsymetricKey(Key):
    def __init__(self, pub_key, priv_key) -> None:
        if not pub_key:
            raise ValueError('"pub_key" can\'t be None.')
        self.pub_key = pub_key
        if pub_key and len(pub_key) != len(priv_key):
                raise ValueError("Different length between public and private key.")
        self.priv_key = priv_key



    def pub_key(self):
        return self.pub_key

    def priv_key(self):
        return self.priv_key


class KeyRegister:
    def __init__(self):
        pass

    def add(self):
        pass

    def copy(self):
        pass

    def discard(self):
        pass

    def remove(self):
        pass

    def union(self):
        pass

    def update(self):
        pass
