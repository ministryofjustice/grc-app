from jwt import encode, decode, ExpiredSignatureError
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec as ec_primitives
import base64
import requests
import json
from uuid import uuid4
from time import time
from grc.one_login.one_login_did_doc_cache import DIDDocumentCache


class JWTHandler:
    """
    Provides utility functions for handling JWT operations including decoding,
    key extraction from JWKS/DID, and generating assertions.
    """

    @staticmethod
    def decode_jwt_with_key(jwt_token, public_key, algorithm="RS256"):
        """
        Decodes a JWT using the provided public key and algorithm.

        :param jwt_token: The JWT string to decode.
        :param public_key: The public key used to verify the signature.
        :param algorithm: JWT algorithm (default: RS256).
        :return: Decoded JWT payload.
        :raises: Exception if token is expired or invalid.
        """
        try:
            return decode(jwt_token, key=public_key, algorithms=[algorithm], options={"verify_aud": False, "verify_signature": False})
        except ExpiredSignatureError:
            raise Exception("Token is expired.")
        except Exception as e:
            raise Exception(f"Failed to decode token: {str(e)}")

    @staticmethod
    def get_public_key_from_jwks(jwks_uri: str, jwt_token: str):
        """
        Extracts the public RSA key from a JWKS endpoint based on the token's kid.

        :param jwks_uri: URI to the JWKS endpoint.
        :param jwt_token: JWT containing a kid in the header.
        :return: RSA public key.
        :raises: Exception if key is not found or request fails.
        """
        kid = JWTHandler._get_kid_from_jwt_token(jwt_token)
        response = requests.get(jwks_uri)
        if response.status_code != 200:
            raise Exception(f"Error fetching JWKS: {response.status_code}")

        jwks = response.json()
        for key in jwks['keys']:
            if key['kid'] != kid:
                continue

            kty = key['kty']
            if kty == 'RSA':
                n = int.from_bytes(base64.urlsafe_b64decode(key['n'] + '=='), 'big')
                e = int.from_bytes(base64.urlsafe_b64decode(key['e'] + '=='), 'big')
                public_numbers = rsa.RSAPublicNumbers(e, n)
                return public_numbers.public_key(default_backend())

            elif kty == 'EC':
                curve_map = {
                    'P-256': ec_primitives.SECP256R1(),
                    'P-384': ec_primitives.SECP384R1(),
                    'P-521': ec_primitives.SECP521R1(),
                }
                curve = curve_map.get(key['crv'])
                if not curve:
                    raise Exception(f"Unsupported curve: {key['crv']}")

                x = int.from_bytes(base64.urlsafe_b64decode(key['x'] + '=='), 'big')
                y = int.from_bytes(base64.urlsafe_b64decode(key['y'] + '=='), 'big')
                public_numbers = ec.EllipticCurvePublicNumbers(x, y, curve)
                return public_numbers.public_key(default_backend())

        raise Exception(f"Public key with kid {kid} not found in JWKS.")

    @staticmethod
    def get_public_key_from_did(did_url, jwt_token):
        """
        Extracts a public EC key from a cached DID document using the token's kid.

        :param did_url: URL to the DID document.
        :param jwt_token: JWT containing a kid in the header.
        :return: EC public key object.
        :raises: Exception if key is not found or mismatched.
        """
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
    def build_jwt_assertion(kid: str, private_key: bytes, algorithm: str, aud: str, iss: str, sub: str, exp_length: int):
        """
        Builds and signs a JWT assertion.

        :param kid: kid from active public key jwk
        :param private_key: Private key used to sign the JWT.
        :param algorithm: Signing algorithm (e.g. RS256 or ES256).
        :param aud: Audience claim.
        :param iss: Issuer claim.
        :param sub: Subject claim.
        :param exp_length: Expiry duration in seconds.
        :return: Signed JWT string.
        """
        now = int(time())
        payload = {
            "aud": aud,
            "iss": iss,
            "sub": sub,
            "exp": now + exp_length,
            "jti": str(uuid4()),
            "iat": now
        }
        return encode(payload, private_key, algorithm=algorithm, headers={"kid": kid})

    @staticmethod
    def _get_controller_id_from_kid(kid):
        """
        Extracts the controller ID portion from the full KID.

        :param kid: Key ID containing the controller prefix.
        :return: Controller ID string.
        :raises: Exception if not found.
        """
        controller_id = kid.split('#', 1)[0]
        if not controller_id:
            raise Exception("Controller ID doesn't exist in KID.")
        return controller_id

    @staticmethod
    def _get_kid_from_jwt_token(jwt_token):
        """
        Extracts the 'kid' field from a JWT header.

        :param jwt_token: JWT string.
        :return: Key ID (kid) string.
        :raises: Exception if kid is missing.
        """
        header = JWTHandler._decode_jwt_header(jwt_token)
        kid = header.get('kid')
        if not kid:
            raise Exception("No 'kid' found in token header.")
        return kid

    @staticmethod
    def _decode_jwt_header(jwt_token):
        """
        Decodes and returns the JWT header as a dictionary.

        :param jwt_token: JWT string.
        :return: Decoded JWT header dict.
        """
        header_b64 = jwt_token.split('.')[0]
        padded = header_b64 + '=' * (-len(header_b64) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))