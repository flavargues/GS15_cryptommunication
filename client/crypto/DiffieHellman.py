import random
import json
from .SHA256 import SHA256
from .ciphers.TripleDES import TripleDES


def dec_to_bin(number: int, length: int) -> str:
    return bin(number)[2:].zfill(length)


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

# generate prime number of bit_length bits with k rounds of Miller-Rabin primality test


def generate_prime(bit_length: int, k: int) -> bytes:
    while True:
        p = random.getrandbits(bit_length)
        if is_prime(p, k):
            return p.to_bytes(bit_length//8, "big")

# generate keys with prime number and generator of length bits


def generate_keys(prime: int, generator: int, length: int) -> tuple:
    private_key = generate_prime(length, 3)
    int_priv = int.from_bytes(private_key, "big")
    public_key = pow(
        generator, int_priv, prime
    ).to_bytes(length//8, "big")
    return public_key, private_key


# Key derivation functions

def derive_master_secret(master_secret: bytes, length: int = 256) -> tuple[bytes, bytes]:
    root_key = SHA256(int.from_bytes(master_secret, "big")+1)
    chain_key = SHA256(int.from_bytes(master_secret, "big")+2)
    return (
        root_key.to_bytes(length//8, "big"),
        chain_key.to_bytes(length//8, "big")
    )


def derive_chain_key(chain_key: bytes, length: int = 256) -> tuple[bytes, bytes]:
    new_chain_key = SHA256(int.from_bytes(chain_key, "big")+1)
    message_key = SHA256(int.from_bytes(chain_key, "big")+2)
    return (
        new_chain_key.to_bytes(length//8, "big"),
        message_key.to_bytes(length//8, "big")
    )


def DiffieHellman(public_key: bytes, private_key: bytes, prime: int, length: int = 1024) -> bytes:
    int_pub = int.from_bytes(public_key, "big")
    int_priv = int.from_bytes(private_key, "big")
    return pow(int_pub, int_priv, prime).to_bytes(length//8, "big")


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


class ExtendedTripleDiffieHellman:
    def __init__(self, id: str, key_size: int, prime: int, generator: int) -> None:
        self.id = id
        self.prime = prime
        self.generator = generator
        self.key_size = key_size
        print("Generating keys for", id, "...")
        self.keys = {
            "identity": generate_keys(prime, generator, self.key_size),
            "signed_prekey": generate_keys(prime, generator, self.key_size),
        }
        print("Identity keys and signed prekeys generated")
        self.recipients: dict = {}
        pass

    # return a dict of my public keys
    def get_my_public_keys(self) -> dict:
        return {
            key: int.from_bytes(value[0], "big") for key, value in self.keys.items()
        }

    # return a list of recipients with keys
    def get_recipients(self) -> list:
        return list(self.recipients.keys())

    # check if we have a recipient with keys
    def have_recipient(self, recipient: str) -> bool:
        return recipient in self.recipients

    # set the public keys of a recipient
    def set_public_keys(self, recipient: str, keys: dict, length: int = 1024) -> None:
        self.recipients[recipient] = {
            "keys": {
                key: value.to_bytes(length//8, "big") for key, value in keys.items()
            },
            "my_keys": {
                "ephemeral": generate_keys(self.prime, self.generator, length)
            },
            "update_ephemeral_keys": False,
        }
        self.recipients[recipient]["keys"]["ephemeral"] = None

    # update the public keys for a recipient
    def update_ephemeral_keys(self, recipient: str) -> None:
        print("Updating my ephemeral keys for ", recipient)
        self.recipients[recipient]["my_keys"]["ephemeral"] = generate_keys(
            self.prime, self.generator, 1024
        )

    def encrypt(self, recipient: str, data: bytes) -> bytes:
        int_data: int = int.from_bytes(data, "big")

        # retrieve the master secret
        secret1 = DiffieHellman(
            self.recipients[recipient]["keys"]["signed_prekey"],
            self.keys["identity"][1],
            self.prime
        )
        secret2 = DiffieHellman(
            self.recipients[recipient]["keys"]["identity"],
            self.recipients[recipient]["my_keys"]["ephemeral"][1],
            self.prime
        )
        secret3 = DiffieHellman(
            self.recipients[recipient]["keys"]["signed_prekey"],
            self.recipients[recipient]["my_keys"]["ephemeral"][1],
            self.prime
        )
        # Skipping secret4 cause we don't use one time keys

        # Derive master secret and chain key
        master_secret = secret1+secret2+secret3
        root_key, chain_key = derive_master_secret(master_secret)
        chain_key, message_key = derive_chain_key(chain_key)

        # Split data into blocks of 8 bytes
        bin_data = dec_to_bin(int_data, (int_data.bit_length()+63)//64*64)
        data_blocks = [bin_data[i:i+64] for i in range(0, len(bin_data), 64)]
        bin_key = dec_to_bin(int.from_bytes(
            message_key, "big"), 256)

        # Decrypt the blocks
        cipher_data = ""
        for block in data_blocks:
            # cipher_data += DES(block, bin_key).encrypt()
            cipher_data += TripleDES(block, bin_key).encrypt()

        # Save the new values
        self.recipients[recipient]["master_secret"] = master_secret
        self.recipients[recipient]["root_key"] = root_key
        self.recipients[recipient]["chain_key"] = chain_key
        self.recipients[recipient]["message_key"] = message_key

        # Generate payload
        message: dict = {
            "sender": self.id,
            "recipient": recipient,
            "protocol": "x3dh",
            "service": {
                "public_key": int.from_bytes(self.recipients[recipient]["my_keys"]["ephemeral"][0], "big"),
            },
            "data": int(cipher_data, 2),
            "checksum": SHA256(int(bin_data, 2))
        }

        return json.dumps(message).encode()

    def decrypt(self, message: bytes) -> bytes:
        payload: dict = json.loads(message.decode())
        if payload["protocol"] != "x3dh":
            return b""
        sender = payload["sender"]
        data: int = payload["data"]
        sender_ephemeral_key = payload["service"]["public_key"].to_bytes(
            self.key_size//8, "big")
        checksum: int = payload["checksum"]

        # retrieve the master secret
        secret1 = DiffieHellman(
            self.recipients[sender]["keys"]["identity"],
            self.keys["signed_prekey"][1],
            self.prime
        )
        secret2 = DiffieHellman(
            sender_ephemeral_key,
            self.keys["identity"][1],
            self.prime
        )
        secret3 = DiffieHellman(
            sender_ephemeral_key,
            self.keys["signed_prekey"][1],
            self.prime
        )
        # Skipping secret4 cause we don't use one time keys

        # Derive master secret and chain key
        master_secret = secret1+secret2+secret3
        root_key, chain_key = derive_master_secret(master_secret)
        chain_key, message_key = derive_chain_key(chain_key)

        # Split data into blocks of 8 bytes
        bin_data = dec_to_bin(data, (data.bit_length()+63)//64*64)
        data_blocks = [bin_data[i:i+64] for i in range(0, len(bin_data), 64)]
        bin_key = dec_to_bin(int.from_bytes(
            message_key, "big"), 256)

        # Decrypt the blocks
        plain_data = ""
        for block in data_blocks:
            # plain_data += DES(block, bin_key).decrypt()
            plain_data += TripleDES(block, bin_key).decrypt()

        # integrity check
        if checksum != SHA256(int(plain_data, 2)):
            return b""

        # check if we need to update our ephemeral keys, if so update them
        if not self.recipients[sender]["keys"]["ephemeral"] or sender_ephemeral_key != self.recipients[sender]["keys"]["ephemeral"]:
            self.update_ephemeral_keys(sender)

        # save the values
        self.recipients[sender]["keys"]["ephemeral"] = sender_ephemeral_key
        self.recipients[sender]["master_secret"] = master_secret
        self.recipients[sender]["root_key"] = root_key
        self.recipients[sender]["chain_key"] = chain_key
        self.recipients[sender]["message_key"] = message_key

        return int(plain_data, 2).to_bytes((len(plain_data)+7)//8, "big")
