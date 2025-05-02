from jwt import encode, decode, ExpiredSignatureError
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.backends import default_backend
import base64
import requests
import json
from uuid import uuid4
from time import time

from grc.one_login.one_login_did_doc_cache import DIDDocumentCache


class JWTHandler:

    @staticmethod
    def decode_jwt_with_key(jwt_token, public_key, algorithm="RS256"):
        try:
            return decode(jwt_token, key=public_key, algorithms=[algorithm], options={"verify_aud": False})
        except ExpiredSignatureError:
            raise Exception("Token is expired.")
        except Exception as e:
            raise Exception(f"Failed to decode token: {str(e)}")

    @staticmethod
    def get_public_key_from_jwks(jwks_uri, jwt_token):
        kid = JWTHandler._get_kid_from_jwt_token(jwt_token)
        response = requests.get(jwks_uri)
        if response.status_code != 200:
            raise Exception(f"Error fetching JWKS: {response.status_code}")

        jwks = response.json()
        for key in jwks['keys']:
            if key['kid'] == kid and key['kty'] == 'RSA':
                n = int.from_bytes(base64.urlsafe_b64decode(key['n'] + '=='), byteorder='big')
                e = int.from_bytes(base64.urlsafe_b64decode(key['e'] + '=='), byteorder='big')
                public_numbers = rsa.RSAPublicNumbers(e, n)
                return public_numbers.public_key(default_backend())

        raise Exception(f"Public key with kid {kid} not found in JWKS.")

    @staticmethod
    def get_public_key_from_did(did_url, jwt_token):
        kid = JWTHandler._get_kid_from_jwt_token(jwt_token)
        controller_id = JWTHandler._get_controller_id_from_kid(kid=kid)

        did_doc = DIDDocumentCache.get_did_document(did_url)

        if did_doc.get('id') != controller_id:
            raise Exception(f"Doc ID doesn't match controller ID.")

        methods = did_doc.get("assertionMethod", [])
        for method in methods:
            if method.get("id") == kid:
                jwk = method.get("publicKeyJwk")
                if jwk and jwk["kty"] == "EC" and jwk["crv"] == "P-256":
                    x = int.from_bytes(base64.urlsafe_b64decode(jwk['x'] + '=='), 'big')
                    y = int.from_bytes(base64.urlsafe_b64decode(jwk['y'] + '=='), 'big')
                    public_numbers = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1())
                    return public_numbers.public_key(default_backend())

        raise Exception(f"Public key with kid {kid} not found in DID document.")

    @staticmethod
    def build_jwt_assertion(private_key: bytes, algorithm: str, aud: str, iss: str, sub: str, exp_length: int):
        now = int(time())
        payload = {
            "aud": aud,
            "iss": iss,
            "sub": sub,
            "exp": now + exp_length,
            "jti": str(uuid4()),
            "iat": now
        }
        return encode(payload, private_key, algorithm=algorithm)

    @staticmethod
    def _get_controller_id_from_kid(kid):
        controller_id = kid.split('#', 1)[0]
        if not controller_id:
            raise Exception("Controller ID doesn't exist in KID.")
        return controller_id

    @staticmethod
    def _get_kid_from_jwt_token(jwt_token):
        header = JWTHandler._decode_jwt_header(jwt_token)
        kid = header.get('kid')
        if not kid:
            raise Exception("No 'kid' found in token header.")
        return kid

    @staticmethod
    def _decode_jwt_header(jwt_token):
        header_b64 = jwt_token.split('.')[0]
        padded = header_b64 + '=' * (-len(header_b64) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))
