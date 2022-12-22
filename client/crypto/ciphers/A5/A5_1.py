class A5_1:
    class LSFR:
        def __init__(
            self, *args, length: int = 0, session_key: str = "", frame_counter: str = ""
        ) -> None:
            # Step 1 Initializing the LSFR
            self.xored_bits = set(*args) - {length - 1}
            self.register = [0] * length

            # Step 2 Clocking LSFR with session key
            for key_bit in session_key:
                self.register.insert(self(key_bit), 0)

            # Step 3 Clocking LSFR with frame counter
            for frame_bit in frame_counter:
                self.register.insert(self(frame_bit), 0)

        def shift(self) -> None:
            feedback = self.register[0]
            for bit_index in self.xored_bits:
                feedback = feedback ^ self.register[bit_index]
            self.register.pop(0)
            self.register.append(feedback)

        def __getitem__(self, item) -> int:
            return self.register[item]

        def __repr__(self) -> str:
            return str(self.register)

        def __call__(self, bit):
            feedback = self.register[-1]
            for bit_index in self.xored_bits:
                feedback = feedback ^ self.register[bit_index]
            return feedback ^ bit

    def __init__(self, key="") -> None:
        if not key != "":
            raise ValueError(f"Seed not defined={key}.")
        for digit in key:
            if digit not in ["0", "1"]:
                raise ValueError(f"Non binary digit in key={key}.")
        self.key = key

    def __call__(self, block, frame_counter):
        self.lsfrs = [
            self.LSFR(
                13,
                16,
                17,
                18,
                length=19,
                session_key=self.key,
                frame_counter=frame_counter,
            ),
            self.LSFR(
                20, 21, length=22, session_key=self.key, frame_counter=frame_counter
            ),
            self.LSFR(
                7,
                20,
                21,
                22,
                length=23,
                session_key=self.key,
                frame_counter=frame_counter,
            ),
        ]

        # Step 4 : Clocking LFSRs with majority vote
        for _ in range(0, 100 - 1):
            self.__shift()

        output = []
        for bit in block:
            random_bit = self.lsfrs[0][0] ^ self.lsfrs[1][0] ^ self.lsfrs[2][0]
            output.append(bit ^ random_bit)
            self.__shift()

        return output

    def __shift(self) -> None:
        clocking_bits = [self.lsfrs[0][8], self.lsfrs[1][10], self.lsfrs[2][10]]
        most_common = max(set(clocking_bits), key=clocking_bits.count)
        for lsfr in self.lsfrs:
            if lsfr[0] == most_common:
                lsfr.shift()

def A51(key, count, bearer, direction, data):
    """
    key : c'est la clé secrète utilisée pour chiffrer et déchiffrer les données. Elle doit être un tableau de 8 octets (64 bits).
    count : c'est le compteur de blocs utilisé pour synchroniser les deux parties qui communiquent. Il doit être un tableau de 2 octets (16 bits).
    bearer : c'est le support de communication utilisé pour transmettre les données. Il doit être un tableau de 2 octets (16 bits).
    direction : c'est une valeur qui indique la direction de la communication. Elle doit être 0 ou 1.
    data : c'est le tableau de données à chiffrer ou déchiffrer. Il doit être un tableau de 8 octets (64 bits).
    """

    # Initialisation des registres
    R1 = [0] * 19
    R2 = [0] * 22
    R3 = [0] * 23

    # Chargement de la clé dans les registres
    for i in range(len(key)):
        R1[i] = key[i]
        R2[i] = key[i]
        R3[i] = key[i]

    # Chargement du compteur et du support de communication dans les registres
    for i in range(len(count)):
        R1[i+8] = count[i]
        R2[i+10] = count[i]
        R3[i+10] = count[i]
    for i in range(len(bearer)):
        R1[i+18] = bearer[i]
        R2[i+21] = bearer[i]
        R3[i+22] = bearer[i]

    # Exécution de l'algorithme de chiffrement
    for i in range(22):
        # Sélection des bits à utiliser pour la fonction de diffusion
        v = (R1[8] + R1[10] + R1[12] + R1[13] + R1[16] + R1[17] + R1[18]) % 2
        w = (R2[10] + R2[12] + R2[13] + R2[14] + R2[17] + R2[18] + R2[21]) % 2
        x = (R3[12] + R3[13] + R3[14] + R3[15] + R3[18] + R3[21] + R3[22]) % 2

        # Calcul de la nouvelle valeur des bits de diffusion
        y = (v + w + x) % 2
        z = (v + w + x + R3[20] + R3[7]) % 2

        # Mise à jour des registres
        R1.insert(0, y)
        R1.pop()
        R2.insert(0, z)
        R2.pop()
        R3.insert(0, x)
        R3.pop()

    # Génération du flux de clés
    K = [0] * 64
    for i in range(64):
        K[i] = (R1[18] + R2[21] + R3[22]) % 2
        # Sélection des bits à utiliser pour la fonction de diffusion
        v = (R1[8] + R
