from math import ceil


class A5_1:
    # Tapped bits - {last bit that we don't xor with itself}
    T1 = {13, 16, 17, 18} - {18}
    T2 = {20, 21} - {21}
    T3 = {7, 20, 21, 22} - {22}

    def __init__(self, key, frame_counter, direction, data) -> None:
        # Cette méthode est le constructeur de la classe. Elle initialise les différents
        # attributs de l'objet et appelle la méthode step1 qui initialise les registres de LFSR.

        self.key = key.bin_list()
        if len(frame_counter) != 22:
            raise ValueError("Frame frame_counterer length should be 22.")
        self.frame_counter = list(frame_counter)
        self.direction = direction  # for duplex only
        self.data = data
        self.step1()

    def encrypt(self):
        # Cette méthode chiffre les données en utilisant le flux de clé produit par
        # l'algorithme.

        return self.output

    def decrypt(self):
        # Cette méthode déchiffre les données en utilisant le flux de clé produit par
        # l'algorithme.

        return self.output

    def step1(self):
        # Cette méthode initialise les trois registres de LFSR à zéro.

        self.R1 = [0] * 19
        self.R2 = [0] * 22
        self.R3 = [0] * 23
        self.Rs = [self.R1, self.R2, self.R3]
        self.step2()

    def step2(self):
        # Cette méthode utilise la clé de chiffrement pour mettre à jour les registres
        # de LFSR. Elle parcourt la clé binaire et pour chaque bit, elle appelle la méthode __feed qui insère le bit dans les registres de LFSR.

        for keybit in self.key:
            keybit = int(keybit)
            self.__feed(keybit, keybit, keybit)
        self.step3()

    def step3(self):
        # Cette méthode utilise le compteur de trame pour mettre à jour les registres
        # de LFSR. Elle parcourt le compteur de trame binaire et pour chaque bit,
        # elle appelle la méthode __feed qui insère le bit dans les registres de LFSR.

        for keybit in self.frame_counter:
            N1, N2, N3 = self.__clock()
            self.__feed(keybit ^ N1, keybit ^ N2, keybit ^ N3)
        self.step4()

    def step4(self):
        # Cette méthode utilise une majorité de vote pour mettre à jour les registres
        # de LFSR. Elle appelle la méthode __irregular_clocking 100 fois pour mettre
        # à jour les registres de LFSR.

        for _ in range(100):
            self.__irregular_clocking()
        self.step5()

    def step5(self):
        # Cette méthode produit le flux de clé qui sera utilisé pour chiffrer/déchiffrer
        # les données. Elle appelle la méthode
        self.key_stream = list()
        for _ in range(228):
            self.key_stream.append(self.__irregular_clocking())
        self.step6()

    def step6(self):
        # Cette méthode chiffre/déchiffre les données en utilisant le flux de clé
        # produit par l'algorithme. Elle parcourt le flux de clé et les données
        # binaires et calcule le XOR de chaque bit. Le résultat est converti en bytes
        # et stocké
        xored_data = str()
        binary_text = [int(x) for x in self.text_to_bits(self.data)]
        for key_stream, data_stream in zip(self.key_stream, binary_text):
            xored_data += str(key_stream ^ data_stream)

        self.output = self.text_from_bits(xored_data)

    def __clock(self):
        # Cette méthode fait faire un cycle à chaque LSFR et renvoie sorties de chacun
        output1 = self.R1[-1]
        for tap in self.T1:
            output1 ^= self.R1[tap]
        output2 = self.R2[-1]
        for tap in self.T2:
            output2 ^= self.R2[tap]
        output3 = self.R3[-1]
        for tap in self.T3:
            output3 ^= self.R3[tap]
        return output1, output2, output3

    def __irregular_clocking(self):
        # Cette méthode effectue le tour d'horloge par vote avec majorité. Elle trouve
        # la valeur de majorité et fait avancer les les LSFR qui l'ont
        outputs = self.__clock()
        if outputs.count(0) >= 2:
            majority = 0
        else:
            majority = 1

        for index, bit in enumerate(outputs):
            if bit == majority:
                self.__shift(index, outputs[index])
        return outputs[0] ^ outputs[1] ^ outputs[2]

    def __shift(self, register_index, input):
        # Cette méthode effectue un shift sur le LSFR donné dans le cadre du tour
        # d'horloge avec vote par majorité
        self.Rs[register_index].pop(0)
        self.Rs[register_index].append(input)

    def __feed(self, N1, N2, N3):
        # Cette méthode insère des bits dans les LSFR
        self.R1.pop(0)
        self.R2.pop(0)
        self.R3.pop(0)
        self.R1.append(N1)
        self.R2.append(N2)
        self.R3.append(N3)

    # Convertir du texte en binaire
    def text_to_bits(self, text):
        bits = bin(int.from_bytes(bytes(text), "big"))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    # Convertir du binaire en texte
    def text_from_bits(self, bits):
        return int(bits, 2).to_bytes(ceil(len(bits) / 8) + 1, "big")
