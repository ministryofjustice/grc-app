from flask import Blueprint, request, jsonify, current_app, redirect

from grc.personal_details import address
from grc.utils.logger import LogLevel, Logger
import urllib.parse
from uuid import uuid4
from jwt import decode, encode
import datetime
import hashlib
import base64

one_login_mock_api = Blueprint('one_login_mock_api', __name__, url_prefix='/one_login/api')
logger = Logger()

mock_auth_context = {}
mock_access_token_context = {}

@one_login_mock_api.route('/.well-known/did.json', methods=['GET'])
def did_doc():
    metadata = {
        "@context" : [ "https://www.w3.org/ns/did/v1", "https://w3id.org/security/jwk/v1" ],
        "id" : "did:web:identity.integration.account.gov.uk",
        "assertionMethod" : [
            {
                "type" : "JsonWebKey",
                "id" : "did:web:identity.integration.account.gov.uk#aa9d4cd51e5cb7e540d8cde10765596cecec928515702b8bb610ed5f9d8467c7",
                "controller" : "did:web:identity.integration.account.gov.uk",
                "publicKeyJwk" : {
                    "kty" : "EC",
                    "crv" : "P-256",
                    "x" : "04ty9SPTNoIoxGDTLO9-VDw0MznbeA657AVbfjze1Ec",
                    "y" : "Edomm5YUSir4Y0_HZl2K9J3DP5A3HrJJEUmqwsmoSZA",
                    "alg" : "ES256"
                }
            },
            {
                "type" : "JsonWebKey",
                "id" : "did:web:identity.integration.account.gov.uk#ac4acbb3cb487cf9f32e29f7d490a8f84b233018035610a399ecc23da86a297a",
                "controller" : "did:web:identity.integration.account.gov.uk",
                "publicKeyJwk" : {
                  "kty" : "EC",
                  "crv" : "P-256",
                  "x" : "rFfCeIaZlBXlALVshryrIwsL08IWDYqC2a5TcoD3pEY",
                  "y" : "ty6kBCVC72XVcwdaNmAGLmGX7tutP1CDZL2flIiA7d4",
                  "alg" : "ES256"
                }
            }
       ]
    }

    return jsonify(metadata)

@one_login_mock_api.route('/.well-known/jwks.json', methods=['GET'])
def jwks():
    metadata = {
      "keys": [
        {
          "kty": "EC",
          "use": "sig",
          "crv": "P-256",
          "kid": "644af598b780f54106ca0f3c017341bc230c4f8373f35f32e18e3e40cc7acff6",
          "x": "5URVCgH4HQgkg37kiipfOGjyVft0R5CdjFJahRoJjEw",
          "y": "QzrvsnDy3oY1yuz55voaAq9B1M5tfhgW3FBjh_n_F0U",
          "alg": "ES256"
        },
        {
          "kty": "EC",
          "use": "sig",
          "crv": "P-256",
          "kid": "e1f5699d068448882e7866b49d24431b2f21bf1a8f3c2b2dde8f4066f0506f1b",
          "x": "BJnIZvnzJ9D_YRu5YL8a3CXjBaa5AxlX1xSeWDLAn9k",
          "y": "x4FU3lRtkeDukSWVJmDuw2nHVFVIZ8_69n4bJ6ik4bQ",
          "alg": "ES256"
        },
        {
          "kty": "RSA",
          "e": "AQAB",
          "use": "sig",
          "kid": "76e79bfc350137593e5bd992b202e248fc97e7a20988a5d4fbe9a0273e54844e",
          "alg": "RS256",
          "n": "lGac-hw2cW5_amtNiDI-Nq2dEXt1x0nwOEIEFd8NwtYz7ha1GzNwO2LyFEoOvqIAcG0NFCAxgjkKD5QwcsThGijvMOLG3dPRMjhyB2S4bCmlkwLpW8vY4sJjc4bItdfuBtUxDA0SWqepr5h95RAsg9UP1LToJecJJR_duMzN-Nutu9qwbpIJph8tFjOFp_T37bVFk4vYkWfX-d4-TOImOOD75G0kgYoAJLS2SRovQAkbJwC1bdn_N8yw7RL9WIqZCwzqMqANdo3dEgSb04XD_CUzL0Y2zU3onewH9PhaMfb11JhsuijH3zRA0dwignDHp7pBw8uMxYSqhoeVO6V0jz8vYo27LyySR1ZLMg13bPNrtMnEC-LlRtZpxkcDLm7bkO-mPjYLrhGpDy7fSdr-6b2rsHzE_YerkZA_RgX_Qv-dZueX5tq2VRZu66QJAgdprZrUx34QBitSAvHL4zcI_Qn2aNl93DR-bT8lrkwB6UBz7EghmQivrwK84BjPircDWdivT4GcEzRdP0ed6PmpAmerHaalyWpLUNoIgVXLa_Px07SweNzyb13QFbiEaJ8p1UFT05KzIRxO8p18g7gWpH8-6jfkZtTOtJJKseNRSyKHgUK5eO9kgvy9sRXmmflV6pl4AMOEwMf4gZpbKtnLh4NETdGg5oSXEuTiF2MjmXE"
        }
      ]
    }
    return jsonify(metadata)

@one_login_mock_api.route('/.well-known/openid-configuration', methods=['GET'])
def discovery():
    try:
        API_BASE_URL = f"{current_app.config.get('BASE_URL', 'http://localhost:3000/')}one_login/api/"

        metadata = {
            "authorization_endpoint": f"{API_BASE_URL}authorize",
            "token_endpoint": f"{API_BASE_URL}token",
            "registration_endpoint": f"{API_BASE_URL}connect/register",
            "issuer": f"{API_BASE_URL}",
            "jwks_uri": f"{API_BASE_URL}.well-known/jwks.json",
            "scopes_supported": [
                "openid",
                "email",
                "phone",
                "offline_access"
            ],
            "response_types_supported": [
                "code"
            ],
            "grant_types_supported": [
                "authorization_code"
            ],
            "code_challenge_methods_supported": [
                "S256"
            ],
            "token_endpoint_auth_methods_supported": [
                "private_key_jwt",
                "client_secret_post"
            ],
            "token_endpoint_auth_signing_alg_values_supported": [
                "RS256",
                "RS384",
                "RS512",
                "PS256",
                "PS384",
                "PS512"
            ],
            "ui_locales_supported": [
                "en",
                "cy"
            ],
            "service_documentation": "https://docs.sign-in.service.gov.uk/",
            "op_policy_uri": "https://signin.integration.account.gov.uk/privacy-notice",
            "op_tos_uri": "https://signin.integration.account.gov.uk/terms-and-conditions",
            "request_parameter_supported": True,
            "trustmarks": f"{API_BASE_URL}trustmark",
            "subject_types_supported": [
                "public",
                "pairwise"
            ],
            "userinfo_endpoint": f"{API_BASE_URL}userinfo",
            "end_session_endpoint": f"{API_BASE_URL}logout",
            "id_token_signing_alg_values_supported": [
                "ES256",
                "RS256"
            ],
            "claim_types_supported": [
                "normal"
            ],
            "claims_supported": [
                "sub",
                "email",
                "email_verified",
                "phone_number",
                "phone_number_verified",
                "wallet_subject_id",
                "https://vocab.account.gov.uk/v1/passport",
                "https://vocab.account.gov.uk/v1/drivingPermit",
                "https://vocab.account.gov.uk/v1/coreIdentityJWT",
                "https://vocab.account.gov.uk/v1/address",
                "https://vocab.account.gov.uk/v1/inheritedIdentityJWT",
                "https://vocab.account.gov.uk/v1/returnCode"
            ],
            "request_uri_parameter_supported": False,
            "backchannel_logout_supported": True,
            "backchannel_logout_session_supported": False
        }
        return jsonify(metadata), 200

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return jsonify({'error': str(e)}), 400


@one_login_mock_api.route('/authorize', methods=['GET'])
def authorize():
    try:
        request_data = request.args
        required_params = ['response_type', 'scope', 'client_id', 'request']
        missing_params = [param for param in required_params if param not in request_data]

        if missing_params:
            raise ValueError("Invalid request")

        request_jwt = request_data.get('request')
        request_object = decode(request_jwt, key=load_public_key(), algorithms=["RS256"], options={"verify_aud": False, "verify_signature": False})

        required_request_params = ['response_type', 'scope', 'client_id', 'redirect_uri', 'nonce', 'aud', 'iss', 'ui_locales', 'vtr', 'claims']
        missing_request_params = [param for param in required_request_params if param not in request_object]

        if missing_request_params:
            raise ValueError("Invalid request")

        vtr = request_object.get('vtr')

        redirect_uri = request_object.get('redirect_uri', '')
        code = str(uuid4())

        mock_auth_context[code] = {
            'nonce': request_object.get('nonce'),
            'vtr': vtr
        }

        success_params = {
            'code': code,
            'state': request_object.get('state')
        }
        redirect_url = f"{redirect_uri}?{urllib.parse.urlencode(success_params)}"
        return redirect(redirect_url)

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return jsonify({'error': str(e)}), 400


@one_login_mock_api.route('/token', methods=['POST'])
def token():
    form_data = request.form
    required_params = ['grant_type', 'redirect_uri', 'client_assertion', 'client_assertion_type', 'code']
    missing_params = [param for param in required_params if param not in form_data]

    if missing_params:
        raise ValueError("Invalid request")

    if form_data.get('grant_type') != 'authorization_code':
        raise ValueError("Invalid request")

    tokens = create_mock_tokens(form_data.get('code'))

    id_token = tokens.get('id_token')
    access_token = tokens.get('access_token')

    try:
        metadata = {
            'access_token': access_token,
            "token_type": "Bearer",
            "expires_in": 180,
            'id_token': id_token
        }

        return jsonify(metadata), 200

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return jsonify({'error': str(e)}), 400


@one_login_mock_api.route('/userinfo', methods=['GET'])
def userInfo():
    try:
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Authorization header missing'}), 401

        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid Authorization header format'}), 401

        access_token = auth_header.split(' ')[1]

        context = mock_access_token_context[access_token]

        if not context:
            raise ValueError("Invalid request")

        vtr = context.get('vtr')

        if not vtr:
            raise ValueError("Invalid request")

        metadata = {
          "sub": "urn:fdc:gov.uk:2022:56P4CMsGh_02YOlWpd8PAOI-2sVlB2nsNU7mcLZYhYw=",
          "email": "test@example.com",
          "email_verified": True,
          "phone_number": "+441406946277",
          "phone_number_verified": True
        }

        if vtr == ['Cl.Cm.P2']:
            metadata["https://vocab.account.gov.uk/v1/coreIdentityJWT"] = encoded_user_core_claim()

            metadata["https://vocab.account.gov.uk/v1/address"] = address_data()

            metadata["https://vocab.account.gov.uk/v1/drivingPermit"] = driving_permit_data()

            metadata["https://vocab.account.gov.uk/v1/passport"] = passport_data()

        return jsonify(metadata), 200

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return jsonify({'error': str(e)}), 400


@one_login_mock_api.route('/logout', methods=['GET'])
def logout():
    try:
        request_data = request.args
        post_logout_redirect_uri = request_data.get('post_logout_redirect_uri', current_app.config.get('BASE_URL'))

        success_params = {
            'state': request_data.get('state', '')
        }

        redirect_url = f"{post_logout_redirect_uri}?{urllib.parse.urlencode(success_params)}"

        return redirect(redirect_url)

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return jsonify({'error': str(e)}), 400


@one_login_mock_api.before_request
def log_request_info():
    logger.log(LogLevel.INFO, f"Mock One Login API request: {request.method} {request.url}")
    return None

def compute_at_hash(access_token: str) -> str:
    """
    Computes the OIDC at_hash from the access token.
    """
    digest = hashlib.sha256(access_token.encode('utf-8')).digest()
    left_most = digest[:16]
    return base64.urlsafe_b64encode(left_most).rstrip(b'=').decode('utf-8')

def create_mock_tokens(code):
    context = mock_auth_context.get(code)
    if not context:
        raise ValueError("Invalid request")

    access_token = str(uuid4())

    mock_access_token_context[access_token] = {
        "vtr": context.get('vtr')
    }

    at_hash = compute_at_hash(access_token)

    now = datetime.datetime.utcnow()
    iat = int(now.timestamp())
    exp = int((now + datetime.timedelta(minutes=5)).timestamp())

    id_token_payload = {
        "at_hash": at_hash,
        "sub": "urn:fdc:gov.uk:2022:VtcZjnU4Sif2oyJZola3OkN0e3Jeku1cIMN38rFlhU4",
        "aud": 'hhJNeUO_5HuSMx7UwmOEjjNLMlE',
        "iss": "http://localhost:3000/one_login/api/",
        "vot": "Cl.Cm",
        "exp": exp,
        "iat": iat,
        "nonce": context.get('nonce'),
        "vtm": "https://oidc.integration.account.gov.uk/trustmark",
        "sid": "dX5xv0XgHh6yfD1xy-ss_1EDK0I",
        "auth_time": iat - 100
    }

    headers = {
        "kid": "644af598b780f54106ca0f3c017341bc230c4f8373f35f32e18e3e40cc7acff6"
    }

    private_key = load_one_login_private_key()
    id_token = encode(id_token_payload, private_key, algorithm="RS256", headers=headers)

    return {
        "id_token": id_token,
        "access_token": access_token
    }

def load_one_login_private_key():
    with open('grc/one_login/mock_api/mock_keys/mock_one_login_private_key.pem', 'r') as f:
        return f.read()

def load_public_key():
    with open('grc/one_login/mock_api/mock_keys/mock_public_key.pem', 'r') as f:
        return f.read()

def address_data() -> list[dict[str, str]]:
    return [
        {
          "uprn": "10022812929",
          "subBuildingName": "FLAT 5",
          "buildingName": "WEST LEA",
          "buildingNumber": "16",
          "dependentStreetName": "KINGS PARK",
          "streetName": "HIGH STREET",
          "doubleDependentAddressLocality": "EREWASH",
          "dependentAddressLocality": "LONG EATON",
          "addressLocality": "GREAT MISSENDEN",
          "postalCode": "HP16 0AL",
          "addressCountry": "GB",
          "validFrom": "2022-01-01"
        },
        {
          "uprn": "10002345923",
          "buildingName": "SAWLEY MARINA",
          "streetName": "INGWORTH ROAD",
          "dependentAddressLocality": "LONG EATON",
          "addressLocality": "NOTTINGHAM",
          "postalCode": "BH12 1JY",
          "addressCountry": "GB",
          "validUntil": "2022-01-01"
        }
    ]

def driving_permit_data() -> list[dict[str, str]]:
    return [
        {
          "expiryDate": "2023-01-18",
          "issueNumber": "5",
          "issuedBy": "DVLA",
          "personalNumber": "DOE99802085J99FG"
        }
    ]

def passport_data() -> list[dict[str,str]]:
    return [
        {
            "documentNumber": "1223456",
            "icaoIssuerCode": "GBR",
            "expiryDate": "2032-02-02"
        }
    ]

def encoded_user_core_claim() -> str:

    core_claim_object = {
      "sub": "urn:fdc:gov.uk:2022:56P4CMsGh_02YOlWpd8PAOI-2sVlB2nsNU7mcLZYhYw=",
      "iss": "https://identity.integration.account.gov.uk/",
      "aud": "YOUR_CLIENT_ID",
      "nbf": 1541493724,
      "iat": 1541493724,
      "exp": 1573029723,
      "vot": "P2",
      "vtm": "https://oidc.integration.account.gov.uk/trustmark",
      "vc": {
        "type": [
          "VerifiableCredential",
          "VerifiableIdentityCredential"
        ],
        "credentialSubject": {
          "name": [
            {
              "validFrom": "2020-03-01",
              "nameParts": [
                {
                  "value": "Alice",
                  "type": "GivenName"
                },
                {
                  "value": "Jane",
                  "type": "GivenName"
                },
                {
                  "value": "Laura",
                  "type": "GivenName"
                },
                {
                  "value": "Doe",
                  "type": "FamilyName"
                }
              ]
            },
            {
              "validUntil": "2020-03-01",
              "nameParts": [
                {
                  "value": "Alice",
                  "type": "GivenName"
                },
                {
                  "value": "Jane",
                  "type": "GivenName"
                },
                {
                  "value": "Laura",
                  "type": "GivenName"
                },
                {
                  "value": "O’Donnell",
                  "type": "FamilyName"
                }
              ]
            }
          ],
          "birthDate": [
            {
              "value": "1970-01-01"
            }
          ]
        }
      }
    }

    headers = {
        "kid": "did:web:identity.integration.account.gov.uk#aa9d4cd51e5cb7e540d8cde10765596cecec928515702b8bb610ed5f9d8467c7"
    }

    private_key = load_one_login_private_key()
    encoded_claims = encode(core_claim_object, private_key, algorithm="RS256", headers=headers)

    return encoded_claims
