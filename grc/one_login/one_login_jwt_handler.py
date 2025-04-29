from jwt import encode, decode, ExpiredSignatureError
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64
import requests
import json
from uuid import uuid4
from time import time

class JWTHandler:

    @staticmethod
    def decode_jwt_header(jwt_token):
        header_b64 = jwt_token.split('.')[0]
        padded = header_b64 + '=' * (-len(header_b64) % 4)
        header_json = base64.urlsafe_b64decode(padded)
        return json.loads(header_json)

    @staticmethod
    def get_kid_from_jwt_token(jwt_token):
        header = JWTHandler.decode_jwt_header(jwt_token)
        return header.get('kid')

    @staticmethod
    def get_public_key_from_jwks(jwks_uri, kid):
        response = requests.get(jwks_uri)
        if response.status_code != 200:
            raise Exception(f"Error fetching JWKS: {response.status_code}")

        jwks = response.json()
        for key in jwks['keys']:
            if key['kid'] == kid and key['kty'] == 'RSA':
                n = int.from_bytes(base64.urlsafe_b64decode(key['n'] + '=='), byteorder='big')
                e = int.from_bytes(base64.urlsafe_b64decode(key['e'] + '=='), byteorder='big')
                public_numbers = rsa.RSAPublicNumbers(e, n)
                public_key = public_numbers.public_key(default_backend())
                return public_key

        raise Exception(f"Public key with kid {kid} not found.")

    @staticmethod
    def decode_jwt_token(jwt_token, jwks_uri, client_id, issuer):
        kid = JWTHandler.get_kid_from_jwt_token(jwt_token)
        public_key = JWTHandler.get_public_key_from_jwks(jwks_uri, kid)
        try:
            decoded_token = decode(jwt_token, key=public_key, algorithms=["RS256"], audience=client_id, issuer=issuer)
            return decoded_token
        except ExpiredSignatureError:
            raise Exception("Token is expired.")
        except Exception as e:
            raise Exception(f"Failed to decode token: {str(e)}")

    @staticmethod
    def build_jwt_assertion(private_key: bytes, algorithm: str, aud: str, iss: str, sub: str, exp_length: int):
        now = int(time())
        jti = str(uuid4())
        payload = {
            "aud": aud,
            "iss": iss,
            "sub": sub,
            "exp": now + exp_length,
            "jti": jti,
            "iat": now
        }
        return encode(payload, private_key, algorithm=algorithm)