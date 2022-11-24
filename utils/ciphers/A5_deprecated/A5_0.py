# A5 Encryption In GSM
# Oliver Damsgaard Jensen
# Kristoffer Alvern Andersen
# June 2017
"""
Section 3.1 - A5/0 - Unencrypted Stream Cipher
A5/0 is the weakest of the A5 versions as it does not offer any encryption at all.
It is a no-operation cipher, that generates the pseudo random bits by negating the
input frame, thus leaving out the XOR function. The result is an algorithm that outputs
the plain text it received as an input. This version is found in third world countries
and countries with UN sanctions[6].
"""

class A5_0:
    def __call__(self, bit):
        return bit