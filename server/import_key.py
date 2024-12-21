from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend

import os
from dotenv import load_dotenv

load_dotenv()
password = os.getenv("password")

if password is None:
    raise ValueError("Password environment variable is not set. Please set it in your .env file.")

# Convert the password to bytes
password_bytes = password.encode('utf-8')


def import_key(file_path):
    with open(file_path, "rb") as f:
        private_key = load_pem_private_key(f.read(), password=password_bytes, backend=default_backend())
        print(private_key)
        return private_key

