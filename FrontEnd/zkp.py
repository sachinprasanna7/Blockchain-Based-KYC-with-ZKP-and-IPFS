# import hashlib
# import os
# import random

# class ZKProof:
#     def __init__(self):
#         self.secret = ""  # Secret used in proof

#     def _hash(self, x):
#         # Creates a SHA-256 hash for the value
#         return hashlib.sha256(x.encode('utf-8')).hexdigest()

#     def generate_proof(self, age):
#         # Users of all ages generate a proof
#         self.secret = "age_above_18" if age >= 18 else "age_below_18"
#         # Commitment based on age threshold
#         self.v = self._hash(self.secret)
#         return self.v

#     def verify(self):
#         # Verify if the commitment is for age 18 or above
#         is_valid = self.v == self._hash("age_above_18")
#         if is_valid:
#             return "Verified: User is 18 or older"
#         else:
#             return "Verification failed: User is under 18"

# Example usage:
# zkp = ZKProof()
# proof = zkp.generate_proof(21)  # Generate proof for age 20
# print(proof)  # This hash will be stored as the ZKP in the Solidity contract
# print(zkp.verify())  # Verification check

import string

class ZKProof:
    def __init__(self):
        self.characters = string.ascii_letters + string.digits  # Letters + digits

    def _simple_hash(self, x):
        # A simple hash function to generate a 32-character pseudo-random string
        hash_value = 0
        for c in x:
            hash_value = (hash_value * 31 + ord(c)) % (10**32)  # Use a multiplier and modulo to get a number
        # Convert hash value into a 32-character string
        result = ''
        for _ in range(32):
            result += self.characters[hash_value % len(self.characters)]  # Pick a character from the list
            hash_value = hash_value // len(self.characters)
        return result

    def generate_proof(self, age):
        # Select the input string based on the age
        if age >= 18:
            input_string = "age_above_18"
        else:
            input_string = "age_below_18"
        return self._simple_hash(input_string)


# Example usage:
simple_hash = ZKProof()
age = 30  # For example
hash_value = simple_hash.generate_proof(age)
print(f"Hash value: {hash_value}")


