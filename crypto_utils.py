from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def load_private_key(private_path: str):
    with open(private_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )
    return private_key


def load_public_key(public_path: str):
    with open(public_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(), backend=default_backend()
        )
    return public_key
