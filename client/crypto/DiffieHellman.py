import random
import json
from SHA256 import SHA256
from ciphers.DES import DES
from ciphers.TripleDES import TripleDES


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


def generate_prime(bit_length: int, k: int) -> bytes:
    while True:
        p = random.getrandbits(bit_length)
        if is_prime(p, k):
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
        # if id == "felix":
        #     self.keys = {'identity': (b'\x0fsi\x00$\xdf\xf0NT\x8e\xf5\x05\xf7Uf\x1b\xd7\x17\x98\x1c\xd9\xa9\x96\xa7\xb07\xb5\xb2\x15\xd0\xf0Y\x9f\xbe\xe7U\x9f\xec\xbcl\x85 \xb5Bl\xa6\x9a\x94\x84\xad\x05!$_\x95\xeaV\\\xffR\xc9\xb9a\x8c\x8b\xac\xd7qA?~\x03\x96\xe7\xa4:@\xfa:x\xfat%W\\\x1b\xf3\xdd\xda\xad\x84\xc8]ow \xce\\\xd26=\xe7\xd2\x1acC\x9e\x88\xcb\x84k\x1d\xa2\x98\x17<\x07\t\xefz\xc1\x9e\x18\xa0\x95\xb0;@', b'\xaaJl8\xd2#}{\xf4\xea\xdd\xc4\x0f!\xa6\x87\x93N\xd4\xffm\x1b\x7f~\xd3(\x14*\xdfx\xad\xe37\xd5\n\xcd\xe56v7t,\xe18?\\\x10\x0e[\xdb\x81Th$\x00y\x18S{\xce85T\xef\xe2lO\xb5E\xb4+\x82\x19C\xdc\x17.\xea\x9c*\xa1Kg\xc03\\&\x18vO\xdc^q\xe4\xeb\x85\x99\x1f\xa0\xf9Q\xc7\xe0q\x04\xa2\x1e\xa3d\x17\xebj\x08\xf4\xb0S\xb6\x10\xbdG\xd8\xb1a\xc6\t|{o'), 'signed_prekey': (
        #         b'>\xdb3\xda*f\xb5\xbf\x94\x07\x11\x17\x1fA\x9f\xdb\xbb\x82\xf4\xe7&\xdb^1^\xb6\xad\xc8\x80T\x7fx\x18?U\xf8-\x1d{@\t\xf7\xd4\xa6J\x0f\x8dl\xafY\x9b\xfb}\xd6\xfc\xb4R9\xa7\x9b\xa8\xdfW\x01Y\x16\x87\xd6\x88\xc28\n\x03@\x96\x11I\xf1gX.\xcdP\xc9\xd3\x82\xb6)\xe4\xc1d\x98\xf9\xcfl4Cat0\xfb\xb1\x08\x98\x1b\xf1\nNNBTA\x93\xa5w\x05\xb9\x08\xc5\xe3\x0b\xe8/\xc3 )\xca\x92', b'0\xc7\xbeM,\x07\x11\xf6\xfeO\x8a%\x1f\x83\x19\x11g!!W\xba\x94\xd3\xcb;\xa6\x94p\x94j\xba\xb4.\xc5Q#\x84\x15z[\x12v\xe0\xf6\xd3\x0cB\xbe\x99\t\x9c\xdd_\x90\xd0\xda\xd4d<}P\xdbj\xb5\xb0\xf4NM\x8f\xae\xa9\x1f\xae\xfc\xe1\xf2\x01\x7f/\t7\xa6"\x9c\x1b\x8a\x15 Ll\xfe\xd6[\x8a\xa1\x99\xae\xa5\xdf\x93\xa3\x0e]@d\x075I\xcb\xb1\x16\xe6~E\xc0\x12\x1a3:\x94\x94,b\x9c\x06-\x1f\x85')}
        # else:
        #     self.keys = {'identity': (b'\x8d\xaf\xc7X0\xb9\xec\x80\xcb\x96\xddyj\xf0\xda\x8d\xe9\xd3+w%\xb1\xa6\xe9\x92\x13t\xf4\xa2\x0c\xfcY&2y7\x8de\xd0\xcc7oQ\xa1\xdd\x16&\xe9\xc6\xd6}7x\t\xe09h\t\xb7\xc5\xaeb\xf4V\xf1\xa9F\xcbKa>;n\x8a\xa9\xe2\x9f\x14\xa6\xf78\xeb\xfbw\xe3\xd5\xd9\xa5\xc0!/\xcd\x10\x86\xdb\xcfzK\x80|\xff&\xf7J\xbd\x8dn\xa6\x8a\x06n\xea\xf4\x0c\xf2K\xc4\xcb\x87.t\x13\x8dp\xfbT0\x02', b'\x14\x14\x01xE9&\x9f\xf2vV\x91x\xf8\xeab\x1d\x84\xe0\x80\x04\xff\xce\xbb-]\xc2\x83\xc2\n\xac=p\xc8\xa1bw6\xbd\x99\xe8\xd0\xa9U:\x9cK\xd2\x88%\x1c\xce\xc2Q\x99H\xc4\x13\x8b\xd6\x14\\\xc2\xa5\xcenl\xbdR;1$s\x1c\xfc\xa7\x17V\x8c}\xe6\xa9\x02Q8\xd7\x9b\xdb&\xbfx&\xa3G\x94\x14\xfc\xb8\xd4\xc0\xa5d`@-\x0e\x90\xf4\x063\x8b[2D\xba\xffO\xf1\xc8\xe2\xc4\x1b\x98\xe1\xb8"\xa4\xe1'), 'signed_prekey': (
        #         b'\x14\xb0\x7f\xc1\x0f`\xe3\x13h>n%\xa1\xee\x9c\xfc]\xca*.m\xcem\xc06C\xa2\xcf\xec\x8e_4\x9e~\xb8\xf6\x80iA\x81\xff\xcf0d\xf7=\xb7\x18\xf4\x9c\xce\xa6\x82\xcf\x94g^-\x8c\x06(\xc1\xd8d\x9b\x1a\x01t5\xfa(%\x03\x82\xd2\xd0\x15\x9b\xcbj?C\x9fo\xf9=\xe9l\xadZ.\x89\xf8\xc5\x94`\'\xe2\xf3\xdb]\x12"6\xfa\x01(d\x0e1\x9f\x98\xf7\xac\x9f\xc8\x97\xdb\xd1\x80\xcdX\xc2\x80=\xe3\xa7(', b'\x15\xbb\x8d\x0f\x7f"\xad\xd3\xcbp\x1f\xb3<\x83\x19\xb7(\x11u\x10\x81\xf1Y\xba\xed\xee\xfd\xa1vr\xd1q.w\x15\xa6\x99\x88\xa5z\x07\xb3\xd0>T mgJ\xfe\x96>\xd0/\xd7\xbe\xbf\xc3\xd2o\xd4\xf0\xfc\xe6bY\xdd0\xca-\xfb\xbdw9\xffkA\xda\x02\x0eh\xf7Ze[\x11\xa5ORd/\xcb\xcd\xe6\x9fo\xc0j\xef \xf4\xf6\xff@\xc3.\x028\x8aKoK\r\x01N\x0f\xb89cc\xfc\nFU\x12\xd7\x89\x03')}
        self.keys = {
            "identity": generate_keys(prime, generator, self.key_size),
            "signed_prekey": generate_keys(prime, generator, self.key_size),
        }
        print("Identity keys and signed prekeys generated")
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

    def update_ephemeral_keys(self, recipient: str) -> None:
        self.recipients[recipient]["my_keys"]["ephemeral"] = generate_keys(
            self.prime, self.generator, 1024
        )

    def encrypt(self, recipient: str, data: bytes) -> bytes:
        # TODO integrity check of entire payload
        int_data: int = int.from_bytes(data, "big")

        # Check if the other part has updated his ephemeral keys
        if self.recipients[recipient]["update_ephemeral_keys"]:
            self.update_ephemeral_keys(recipient)
            self.recipients[recipient]["update_ephemeral_keys"] = False

        # Do the DiffieHellman to retrieve master secret
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
            "checksum": SHA256(int(cipher_data, 2))
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

        # Do the DiffieHellman to retrieve master secret
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

        self.recipients[sender]["update_ephemeral_keys"] = True if sender_ephemeral_key != self.recipients[sender]["keys"]["ephemeral"] else False

        # save the values
        self.recipients[sender]["keys"]["ephemeral"] = sender_ephemeral_key
        self.recipients[sender]["master_secret"] = master_secret
        self.recipients[sender]["root_key"] = root_key
        self.recipients[sender]["chain_key"] = chain_key
        self.recipients[sender]["message_key"] = message_key

        return int(plain_data, 2).to_bytes((len(plain_data)+7)//8, "big")


# if __name__ == "__main__":
#     p = 153638087954137989778471789835301014651859930427694693921508980917981440238722838596048262061563360383100385894944259397337774006127904648340605750612438505445921354889618267380101183802339656702046105940078840154453761657454458085362955304574968675250816978793272838820646951107616078955642621700031035724701
#     g = 9008
#     x3dh: ExtendedTripleDiffieHellman = ExtendedTripleDiffieHellman(
#         "felix", 1024, p, g,)
#     x3dh2: ExtendedTripleDiffieHellman = ExtendedTripleDiffieHellman(
#         "felix2", 1024, p, g)

#     x3dh.set_public_keys(
#         "felix2",
#         x3dh2.get_my_public_keys())

#     x3dh2.set_public_keys(
#         "felix",
#         x3dh.get_my_public_keys())

#     print(x3dh.recipients)

#     encrypted_payload = x3dh.encrypt(
#         "felix2", b"hdjskfcjedc!")
#     decrypted_payload = x3dh2.decrypt(encrypted_payload)
#     print(decrypted_payload.decode())

#     encrypted_payload = x3dh.encrypt(
#         "felix2", b"cjkjfdcxv!")
#     decrypted_payload = x3dh2.decrypt(encrypted_payload)
#     print(decrypted_payload.decode())

#     encrypted_payload = x3dh.encrypt(
#         "felix2", b"fjherngjknvkrjebsdhngv nerfd s v jejksfdgbjhverebskfdngvkjreks,dkgjnvjerklqdskjgjvrneqksdgjkvnerjkqsef<c!")
#     decrypted_payload = x3dh2.decrypt(encrypted_payload)
#     print(decrypted_payload.decode())

#     encrypted_payload = x3dh2.encrypt(
#         "felix", b"dghcejkhshfjcjhzr vhgvjhkllnbjkhvklj,nlbjklm,lkdbvcnez,lfbchzejknqsfjkchzeznkflkcjkzebklqfC?ZEKFCnjkbkjbkjnlknlknlmknjlkkkdlmfckjerqsnd fncbjerhdnsqlfmkcerbqldjkflerhdbqfvernbdqsg nvjhrehqdbfkjcnrkjegfnvkjerbkjgqv n er n!")
#     decrypted_payload = x3dh.decrypt(encrypted_payload)
#     print(decrypted_payload.decode())

#     encrypted_payload = x3dh.encrypt(
#         "felix2", b"fjherngjknvkrjebsdhngv nerfd s v jejksfdgbjhverebskfdngvkjreks,dkgjnvjerklqdskjgjvrneqksdgjkvnerjkqsef<c!")
#     decrypted_payload = x3dh2.decrypt(encrypted_payload)
#     print(decrypted_payload.decode())

#     encrypted_payload = x3dh2.encrypt(
#         "felix", b"dghcejkhshfjcjhzr vhgvjhkllnbjkhvklj,nlbjklm,lknjkbkjbkjnlknlknlmknjlkkkdlmfckjerqsnd fncbjerhdnsqlfmkcerbqldjkflerhdbqfvernbdqsg nvjhrehqdbfkjcnrkjegfnvkjerbkjgqv n er n!")
#     decrypted_payload = x3dh.decrypt(encrypted_payload)
#     print(decrypted_payload.decode())

#     pass
