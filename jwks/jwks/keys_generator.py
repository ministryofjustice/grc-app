from uuid import uuid4
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from typing import Any
import base64
from cryptography.hazmat.backends import default_backend

class KeysGenerator:

    @staticmethod
    def generate_jwt_keypair_with_kid():
        kid = KeysGenerator._generate_kid()
        private_key, public_key = KeysGenerator._create_private_public_key_pair()
        private_key = private_key.decode('utf-8')
        public_jwk = KeysGenerator._generate_jwk_from_pem(public_key_pem=public_key, kid=kid)
        return {'kid':kid, 'private_key_pem': private_key, 'public_key_jwk': public_jwk}

    @staticmethod
    def _create_private_public_key_pair() -> tuple[bytes, bytes]:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,  # or PKCS8
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key = private_key.public_key()

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem

    @staticmethod
    def _generate_jwk_from_pem(public_key_pem: bytes, kid:str) -> dict[str, Any]:

        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )

        public_numbers = public_key.public_numbers()
        e = public_numbers.e
        n = public_numbers.n

        def to_base64url(n):
            b = n.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
            return base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")

        return {
            "kty": "RSA",
            "use": "sig",
            "alg": "RS256",
            "kid": kid,
            "n": to_base64url(n),
            "e": to_base64url(e)
        }


    @staticmethod
    def _generate_kid() -> str:
        return str(uuid4())
