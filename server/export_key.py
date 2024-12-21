import os
from dotenv import load_dotenv

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    BestAvailableEncryption,
)

load_dotenv()
password = os.getenv('password')

if password is None:
    raise ValueError("Password environment variable is not set. Please set it in your .env file.")

# Convert the password to bytes
password_bytes = password.encode('utf-8')


# Export the private key for "targets" to a file
def export_key(private_key, name):

    pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=BestAvailableEncryption(password_bytes),  # Use encryption for better security
    )

    with open(f"./keys/{name}_private_key.pem", "wb") as f:
        f.write(pem)

    print(f"Private key saved as '{name}_key.pem'")
