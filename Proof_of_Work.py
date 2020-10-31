import string
import random
import hashlib
import time

example_challenge = "Hoi zäme"

def generation (challenge=example_challenge,size=25):
    answer = "".join(random.choice(string.ascii_lowercase+string.ascii_uppercase+string.digits) for x in range(size))

    attempt = challenge + answer
    return attempt, answer

shaHash = hashlib.sha256()

def testAttempt():
    Found = False
    start = time.time()
    while Found == False:
        attempt, answer = generation()
        shaHash = hashlib.sha256(attempt.encode("utf-8"))
        solution = shaHash.hexdigest()
        if solution.startswith("00000"):
            TimeTook = time.time() -start
            print("Solution:", solution)
            print("Time took:",TimeTook)
            print("Attempt:", attempt)
            print("Test:", hashlib.sha256(attempt.encode("utf-8")).hexdigest())
            Found=True

testAttempt()


