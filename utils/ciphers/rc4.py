from utils.lsfr import LSFR


class A5_1:
    def __init__(self, seed="") -> None:
        if not seed != "":
            raise ValueError(f"Seed not defined={seed}.")
        for digit in seed:
            if digit not in ["0", "1"]:
                raise ValueError(f"Non binary digit in seed={seed}.")

        self.lsfr = [
            LSFR(19, 0, 1, 2, 5, seed=seed[0:18], manual_shift=True),
            LSFR(22, 0, 1, seed=seed[19:40], manual_shift=True),
            LSFR(23, 0, 1, 2, 15, seed=seed[41:63], manual_shift=True),
        ]

    def shift(self):
        l0 = self.lsfr[0].register[10]
        l1 = self.lsfr[1].register[11]
        l2 = self.lsfr[2].register[12]
        lsfrs = [l0, l1, l2]
        most_common = max(set(lsfrs), key=lsfrs.count)

        if l0 == most_common:
            self.lsfr[0].shift()
        if l1 == most_common:
            self.lsfr[1].shift()
        if l2 == most_common:
            self.lsfr[2].shift()
