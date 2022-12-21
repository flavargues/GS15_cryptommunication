import random


class CryptographicConstantBaseClass:
    def __eq__(self, __o: object) -> bool:
        return type(__o) == type(self) and hash(self) == hash(__o)


class CryptographicKeyBaseClass(CryptographicConstantBaseClass):
    @classmethod
    def autoSecureKeyGenerator(cls, length=64) -> int:
        key = generate_prime(length, 100000)
        return key


def is_prime(n: int, k: int) -> bool:
    if n <= 1:
        return False

    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)

        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def generate_prime(bit_length: int, k: int) -> int:
    while True:
        p = random.getrandbits(bit_length)

        if is_prime(p, k):
            return p


class SymetricKey(CryptographicKeyBaseClass):
    def __init__(self, key) -> None:
        if not key:
            key = self.autoSecureKeyGenerator()
        self.key = key

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return "SYM=" + str(self.key)


class AsymetricKey(CryptographicKeyBaseClass):
    def __init__(self, pub_key) -> None:
        self.priv_key = None
        if not pub_key:
            pub_key = self.autoSecureKeyGenerator()
            priv_key = self.autoSecureKeyGenerator()
        self.pub_key = pub_key
        return pub_key, priv_key

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
            raise ValueError(
                "SHA-256 hash should be None or empty, and of length 256.")
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
