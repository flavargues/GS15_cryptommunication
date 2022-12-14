class CryptographicConstantBaseClass:
    def __eq__(self, __o: object) -> bool:
        return type(__o) == type(self) and hash(self) == hash(__o)


class CryptographicKeyBaseClass(CryptographicConstantBaseClass):
    pass


class SymetricKey(CryptographicKeyBaseClass):
    def __init__(self, key) -> None:
        if not key:
            raise ValueError('"key" can\'t be None.')
        self.key = key

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return "SYM=" + str(self.key)


class AsymetricKey(CryptographicKeyBaseClass):
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


class Hash(CryptographicConstantBaseClass):
    def __init__(self, hash) -> None:
        if not hash or len(hash) != 256:
            raise ValueError("SHA-256 hash should be None or empty, and of length 256.")
        self.value = hash

    def __hash__(self) -> int:
        return int(self.value)

    def __repr__(self) -> str:
        return "HASH=" + str(self.value)


class Signature(CryptographicConstantBaseClass):
    def __init__(self, signature) -> None:
        if not signature or len(signature) > 0:
            raise ValueError("Signature shouldn't be None or empty.")
        self.value = signature

    def __hash__(self) -> int:
        return int(self.value)

    def __repr__(self) -> str:
        return "SIGN=" + str(self.value)


class AuthentificationKey(CryptographicConstantBaseClass):
    def __init__(self, key) -> None:
        self.value = key

    def __hash__(self) -> int:
        return int(self.value)

    def __repr__(self) -> str:
        return "AUTH=" + str(self.value)
