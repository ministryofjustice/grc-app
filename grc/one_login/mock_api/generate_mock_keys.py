from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

def generate_and_write_keys():
    os.makedirs("grc/one_login/mock_api/mock_keys", exist_ok=True)

    one_login_public_pem, one_login_private_pem = create_key_pair_pem()
    public_pem, private_pem = create_key_pair_pem()

    with open("grc/one_login/mock_api/mock_keys/mock_one_login_public_key.pem", "wb") as f:
        f.write(one_login_public_pem)

    with open("grc/one_login/mock_api/mock_keys/mock_one_login_private_key.pem", "wb") as f:
        f.write(one_login_private_pem)

    with open("grc/one_login/mock_api/mock_keys/mock_public_key.pem", "wb") as f:
        f.write(public_pem)

    with open("grc/one_login/mock_api/mock_keys/mock_private_key.pem", "wb") as f:
        f.write(private_pem)

    return private_pem, public_pem

def create_key_pair_pem():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return public_pem, private_pem