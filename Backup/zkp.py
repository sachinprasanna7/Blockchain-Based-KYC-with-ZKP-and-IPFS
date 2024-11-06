import hashlib
import os
import random

class ZKProof:
    def __init__(self):
        self.N = 20  # Arbitrary range for randomness
        self.salt = os.urandom(16)  # Salt to add randomness

    def _hash(self, x):
        # Creates a unique hash for the value combined with the salt
        return hashlib.sha256(x.encode('utf-8') + self.salt).hexdigest()

    def generate_proof(self, age):
        # Users of all ages generate a proof
        self.secret = "age_above_18" if age >= 18 else "age_below_18"
        self.v = self._hash(self.secret)  # Commitment based on age threshold
        r = str(random.randint(1, self.N))
        self.x = self._hash(r)
        return self.x

    def verify(self):
        # Verify if the commitment is for age 18 or above
        is_valid = self.v == self._hash("age_above_18")
        if is_valid:
            return "Verified: User is 18 or older"
        else:
            return "Verification failed: User is under 18"

# # Usage Example
# zkp = ZKProof()

# # User inputs age
# user_age = int(input("Enter your age: "))
# proof = zkp.generate_proof(user_age)
# print("Proof generated:", proof)

# # Verifier checks the proof
# verification_result = zkp.verify()  # The verifier uses "age_above_18" as the commitment to check against
# print(verification_result)