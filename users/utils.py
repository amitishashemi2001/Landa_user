import random

def generate_verification_token():
    return str(random.randint(100000, 999999))
