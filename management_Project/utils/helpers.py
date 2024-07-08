import hashlib
import random
import string

def generate_random_string(length=12):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()
