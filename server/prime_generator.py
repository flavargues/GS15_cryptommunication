import random


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


def get_generator(prime: int, number: int = 1000) -> int:
    generators = []
    for g in range(2, prime):
        if pow(g, prime-1, prime) == 1:
            if len(generators) >= number:
                break
            generators.append(g)

    r = random.randint(0, number-1)
    generator = generators[r]
    return generator
