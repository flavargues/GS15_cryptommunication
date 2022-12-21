import random
import json
from .SHA256 import SHA256
from .ciphers.DES import DES


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


def generate_prime(bit_length: int, k: int) -> bytes:
    while True:
        p = random.getrandbits(bit_length)
        if is_prime(p, k):
            print("Prime found")
            return p.to_bytes(bit_length//8, "big")


def fast_exponentiation(base: int, exponent: int, modulus: int) -> int:
    result = 1
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    return result


def generate_keys(prime: int, generator: int, length: int) -> tuple:
    private_key = generate_prime(length, 1000)
    int_priv = int.from_bytes(private_key, "big")
    public_key = pow(
        generator, int_priv, prime
    ).to_bytes(length//8, "big")
    return public_key, private_key


# Key derivation functions

def derive_master_secret(master_secret: bytes) -> tuple:
    root_key = SHA256(master_secret+b"01")
    chain_key = SHA256(master_secret+b"02")
    return root_key, chain_key


def derive_chain_key(chain_key: bytes) -> tuple:
    new_chain_key = SHA256(chain_key+b"01")
    message_key = SHA256(chain_key+b"02")
    return new_chain_key, message_key


def DiffieHellman(private_key: bytes, public_key: bytes) -> bytes:
    int_priv = int.from_bytes(private_key, "big")
    int_pub = int.from_bytes(public_key, "big")
    return pow(int_pub, int_priv, 23).to_bytes(1024, "big")


recipients = {
    "alice": {
        "my_keys": {
            "ephemeral": (b"\x00", b"\x00"),  # (public_key, private_key)
        },
        "keys": {
            "identity": b"\x00",  # public_key
            "ephemeral": b"\x00",  # public_key
            "signed_prekey": b"\x00",  # public_key
        },
        "master_secret": b"\x00",
        "root_key": b"\x00",
        "chain_key": b"\x00",
        "message_key": b"\x00",
    },
    "bob": {
        "my_keys": {
            "ephemeral": (b"\x00", b"\x00"),  # (public_key, private_key)
        },
        "keys": {
            "identity": b"\x00",  # public_key
            "ephemeral": b"\x00",  # public_key
            "signed_prekey": b"\x00",  # public_key
        },
        "master_secret": b"\x00",
        "root_key": b"\x00",
        "chain_key": b"\x00",
        "message_key": b"\x00",
    }
}


# def generate_keys() -> tuple:
#     print('Generating keys...')
#     private_key = generate_prime(1024, 100000)
#     public_key = generate_prime(1024, 100000)
#     return public_key, private_key

# Key generation functions


class ExtendedTripleDiffieHellman:
    def __init__(self, id: str, prime: int, generator: int) -> None:
        # self.p = generate_prime(1024, 100000)
        # Generate keysss
        self.id = id
        self.prime = prime
        self.generator = generator
        self.keys = {
            "identity": generate_keys(prime, generator, 1024),
            "signed_prekey": generate_keys(prime, generator, 1024),
        }
        print({
            key: [value.hex() for value in self.keys[key]] for key in self.keys
        })
        self.recipients: dict = {}
        pass

    def get_my_public_keys(self) -> dict:
        return {
            key: int.from_bytes(value[0], "big") for key, value in self.keys.items()
        }

    def get_recipients(self) -> list:
        return list(self.recipients.keys())

    def have_recipient(self, recipient: str) -> bool:
        return recipient in self.recipients

    def set_public_keys(self, recipient: str, keys: dict, length: int) -> None:
        self.recipients[recipient] = {
            "keys": {
                key: value.to_bytes(length//8, "big") for key, value in keys.items()
            },
            "my_keys": {
                "ephemeral": generate_keys(self.prime, self.generator, length)
            },
            "update_ephemeral_keys": False,
        }

    def update_ephemeral_keys(self, recipient: str) -> None:
        self.recipients[recipient]["my_keys"]["ephemeral"] = generate_keys(
            self.prime, self.generator, 1024
        )

    def encrypt(self, recipient: str, data: bytes) -> bytes:
        # TODO integrity check of entire payload

        # Check if the other part has updated his ephemeral keys
        if self.recipients[recipient]["update_ephemeral_keys"]:
            self.update_ephemeral_keys(recipient)
            self.recipients[recipient]["update_ephemeral_keys"] = False

        # Do the DiffieHellman to retrieve master secret
        secret1 = DiffieHellman(
            self.keys["identity"][1],
            self.recipients[recipient]["keys"]["signed_prekey"],
        )
        secret2 = DiffieHellman(
            self.recipients[recipient]["my_keys"]["ephemeral"][1],
            self.recipients[recipient]["keys"]["identity"],
        )
        secret3 = DiffieHellman(
            self.recipients[recipient]["my_keys"]["ephemeral"][1],
            self.recipients[recipient]["keys"]["signed_prekey"],
        )
        # Skipping secret4 cause we don't use one time keys

        # Derive master secret and chain key
        master_secret = secret1+secret2+secret3
        root_key, chain_key = derive_master_secret(master_secret)
        chain_key, message_key = derive_chain_key(chain_key)

        cipher_data = DES(data, message_key).encrypt()

        # Save the new values
        self.recipients[recipient]["master_secret"] = master_secret
        self.recipients[recipient]["root_key"] = root_key
        self.recipients[recipient]["chain_key"] = chain_key
        self.recipients[recipient]["message_key"] = message_key

        # Generate payload
        message: dict = {
            "recipient": recipient,
            "protocol": "x3dh",
            "service": {
                "public_key": self.recipients[recipient]["my_keys"]["ephemeral"][0],
            },
            "data": cipher_data,
            "checksum": SHA256(data)
        }

        return json.dumps(message).encode()

    def decrypt(self, message: bytes) -> bytes:
        payload: dict = json.loads(message.decode())
        if payload["protocol"] != "x3dh":
            return b""
        sender = payload["sender"]
        data = payload["data"].encode()
        public_key = payload["service"]["public_key"].encode()
        checksum = payload["checksum"].encode()

        # Do the DiffieHellman to retrieve master secret
        secret1 = DiffieHellman(
            self.recipients[sender]["keys"]["identity"],
            self.keys["signed_prekey"][1],
        )
        secret2 = DiffieHellman(
            self.recipients[sender]["keys"]["ephemeral"],
            self.keys["identity"][1],
        )
        secret3 = DiffieHellman(
            self.recipients[sender]["keys"]["ephemeral"],
            self.keys["signed_prekey"][1],
        )
        # Skipping secret4 cause we don't use one time keys

        # Derive master secret and chain key
        master_secret = secret1+secret2+secret3
        root_key, chain_key = derive_master_secret(master_secret)
        chain_key, message_key = derive_chain_key(chain_key)

        # Decrypt the data
        plain_data = DES(data, message_key).decrypt()

        self.recipients[sender]["update_ephemeral_keys"] = True if public_key != self.recipients[sender]["keys"]["ephemeral"] else False

        # save the values
        self.recipients[sender]["public_key"] = public_key
        self.recipients[sender]["master_secret"] = master_secret
        self.recipients[sender]["root_key"] = root_key
        self.recipients[sender]["chain_key"] = chain_key
        self.recipients[sender]["message_key"] = message_key

        # integrity check
        if checksum == SHA256(plain_data):
            return plain_data
        else:
            return b""


if __name__ == "__main__":
    p = 153638087954137989778471789835301014651859930427694693921508980917981440238722838596048262061563360383100385894944259397337774006127904648340605750612438505445921354889618267380101183802339656702046105940078840154453761657454458085362955304574968675250816978793272838820646951107616078955642621700031035724701
    g = 9008
    x3dh = ExtendedTripleDiffieHellman("felix", p, g,)
    x3dh2 = ExtendedTripleDiffieHellman("felix2", p, g)
    pass
