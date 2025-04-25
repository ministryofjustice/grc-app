from authlib.integrations.flask_client import OAuth
from flask import Flask, request, redirect, url_for, session, render_template
import requests
import logging
import sys
from cryptography.hazmat.primitives import serialization
import jwt
import json
import time
import uuid
from urllib.parse import urlencode
from jose import jwk

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "your-secret-key"
oauth = OAuth(app)

class Config:
    ISSUER = "https://oidc.integration.account.gov.uk"
    CLIENT_ID = "o8bkoFoPZvyzlxGJ6SRVlhprYkM"  # Replace with your actual client_id
    PRIVATE_KEY_PATH = "grc-onelogin-private.pem"
    REDIRECT_URI = "http://localhost:5000/oidc/authorization-code/callback"
    SCOPE = "openid phone email"
    TOKEN_AUTH_METHOD = "private_key_jwt"
    REQUIRE_JAR = False
    IV_ISSUER = "https://identity.integration.account.gov.uk/"
    IDENTITY_VTR = "P2.Cl.Cm"
    IMMEDIATE_REDIRECT = True
    IDENTITY_SUPPORTED = True

config = Config()

def get_discovery_metadata():
    discovery_url = f"{config.ISSUER}/.well-known/openid-configuration"
    response = requests.get(discovery_url)
    logger.info(f"Discovery URL: {discovery_url}")
    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Response Text: {response.text}")
    if response.status_code != 200:
        raise Exception(f"Discovery failed: {response.status_code} - {response.text}")
    return response.json()

try:
    metadata = get_discovery_metadata()
except Exception as e:
    logger.error(f"Failed to initialize metadata: {e}")
    raise

try:
    with open(config.PRIVATE_KEY_PATH, "rb") as f:
        logger.info(f"Private key loaded from {config.PRIVATE_KEY_PATH}")
except Exception as e:
    logger.error(f"Failed to load private key: {e}")
    raise

def create_jwt_assertion():
    now = int(time.time())
    payload = {
        "aud": "https://oidc.integration.account.gov.uk/token",
        "iss": config.CLIENT_ID,
        "sub": config.CLIENT_ID,
        "exp": now + 300,
        "jti": str(uuid.uuid4()),
        "iat": now
    }
    with open(config.PRIVATE_KEY_PATH, "rb") as f:
        private_key = f.read()
    return jwt.encode(payload, private_key, algorithm="RS256")

def create_request_object(vtr="Cl.Cm"):
    nonce = str(uuid.uuid4())
    state = str(uuid.uuid4())
    session["nonce"] = nonce
    session["state"] = state

    request_payload = {
        "aud": "https://oidc.integration.account.gov.uk/authorize",
        "iss": config.CLIENT_ID,
        "response_type": "code",
        "client_id": config.CLIENT_ID,
        "redirect_uri": config.REDIRECT_URI,
        "scope": config.SCOPE,
        "state": state,
        "nonce": nonce,
        "vtr": [vtr],
        "ui_locales": "en",
        "claims": {
            "userinfo": {
                "https://vocab.account.gov.uk/v1/coreIdentityJWT": None,
                "https://vocab.account.gov.uk/v1/address": None,
                "https://vocab.account.gov.uk/v1/returnCode": None
            }
        }
    }
    with open(config.PRIVATE_KEY_PATH, "rb") as f:
        private_key = f.read()
    request_jwt = jwt.encode(request_payload, private_key, algorithm="RS256")
    logger.debug(f"Created request object: {request_payload}")
    return request_jwt

def fetch_token(code):
    token_url = metadata["token_endpoint"]
    assertion = create_jwt_assertion()
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.REDIRECT_URI,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": assertion
    }
    logger.debug(f"POST to {token_url} with body: {data}")
    response = requests.post(
        token_url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    logger.debug(f"Response Status: {response.status_code}, Body: {response.text}")
    if response.status_code != 200:
        raise Exception(f"Token request failed: {response.status_code} - {response.text}")
    return response.json()

def fetch_user_info(access_token):
    userinfo_url = metadata["userinfo_endpoint"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    logger.debug(f"GET to {userinfo_url} with headers: {headers}")
    response = requests.get(userinfo_url, headers=headers)
    logger.info(f"Userinfo Response Status: {response.status_code}")
    logger.info(f"Userinfo Response Body: {json.dumps(response.json(), indent=2)}")
    if response.status_code != 200:
        raise Exception(f"Userinfo request failed: {response.status_code} - {response.text}")
    return response.json()

oauth.register(
    name="oidc",
    client_id=config.CLIENT_ID,
    client_secret=None,
    server_metadata_url=f"{config.ISSUER}/.well-known/openid-configuration",
    client_kwargs={"scope": config.SCOPE}
)

def get_identity_signing_public_key(kid):
    did_url = "https://identity.integration.account.gov.uk/.well-known/did.json"
    response = requests.get(did_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch DID document: {response.status_code}")
    did_doc = response.json()

    logger.debug(f"Searching for kid: {kid}")
    for assertion_method in did_doc.get("assertionMethod", []):
        assertion_id = assertion_method["id"]
        logger.debug(f"Checking assertionMethod id: {assertion_id}")
        if assertion_id == kid:
            jwk_data = assertion_method["publicKeyJwk"]
            if jwk_data["kty"] == "EC" and jwk_data["alg"] == "ES256":
                key = jwk.construct(jwk_data, algorithm="ES256")
                public_key_pem = key.to_pem()
                return serialization.load_pem_public_key(public_key_pem)
    raise Exception(f"No matching EC key found for kid: {kid}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/authorize/auth-only")
def authorize_auth_only():
    request_object = create_request_object(vtr="Cl.Cm")
    auth_params = {
        "response_type": "code",
        "scope": config.SCOPE,
        "client_id": config.CLIENT_ID,
        "request": request_object
    }
    auth_url = f"{metadata['authorization_endpoint']}?{urlencode(auth_params)}"
    logger.debug(f"Redirecting to {auth_url}")
    return redirect(auth_url)

@app.route("/authorize/prove-identity")
def authorize_prove_identity():
    request_object = create_request_object(vtr="P2.Cl.Cm")
    auth_params = {
        "response_type": "code",
        "scope": config.SCOPE,
        "client_id": config.CLIENT_ID,
        "request": request_object
    }
    auth_url = f"{metadata['authorization_endpoint']}?{urlencode(auth_params)}"
    logger.debug(f"Redirecting to {auth_url}")
    return redirect(auth_url)

@app.route("/oidc/authorization-code/callback")
def callback():
    try:
        logger.info("Back in callback")
        if "error" in request.args:
            error = request.args["error"]
            desc = request.args.get("error_description", "")
            raise Exception(f"{error} - {desc}")

        nonce = session.get("nonce")
        state = session.get("state")
        code = request.args.get("code")
        if not code:
            raise Exception("No code received in callback")

        token = fetch_token(code)

        id_token = token.get("id_token")
        access_token = token.get("access_token")
        id_token_claims = jwt.decode(
            id_token,
            options={"verify_signature": False, "verify_aud": False}
        )
        if id_token_claims.get("nonce") != nonce:
            raise Exception("Nonce mismatch")

        response = app.make_response("Processing complete")
        response.set_cookie("id-token", id_token, httponly=True)

        userinfo = fetch_user_info(access_token)
        id_token_sub = id_token_claims["sub"]

        core_identity_payload = None
        return_code_value = userinfo.get("https://vocab.account.gov.uk/v1/returnCode")

        if "https://vocab.account.gov.uk/v1/coreIdentityJWT" in userinfo:
            core_identity_jwt = userinfo["https://vocab.account.gov.uk/v1/coreIdentityJWT"]
            logger.debug(f"Core Identity JWT: {core_identity_jwt}")
            header = jwt.get_unverified_header(core_identity_jwt)
            kid = header["kid"]
            logger.debug(f"JWT Header: {header}")
            unverified_claims = jwt.decode(
                core_identity_jwt,
                options={"verify_signature": False, "verify_aud": False, "verify_iss": False}
            )
            logger.debug(f"Unverified coreIdentityJWT claims: {json.dumps(unverified_claims, indent=2)}")
            public_key = get_identity_signing_public_key(kid)
            try:
                core_identity_payload = jwt.decode(
                    core_identity_jwt,
                    public_key,
                    algorithms=["ES256"],
                    issuer=config.IV_ISSUER,
                    audience=config.CLIENT_ID
                )
            except jwt.InvalidAudienceError as e:
                logger.error(f"JWT Invalid Audience Error: {e}, expected: {config.CLIENT_ID}, claims: {unverified_claims}")
                raise
            except jwt.InvalidIssuerError as e:
                logger.error(f"JWT Invalid Issuer Error: {e}, expected: {config.IV_ISSUER}, claims: {unverified_claims}")
                raise
            except jwt.PyJWTError as e:
                logger.error(f"JWT Decode Error: {e}, claims: {unverified_claims}")
                raise

            vtr_to_check = config.IDENTITY_VTR.split(".")[0] if config.IDENTITY_VTR else None  # Extract P2
            logger.debug(f"Comparing vot: {core_identity_payload.get('vot')} against expected: {vtr_to_check}")
            if core_identity_payload["sub"] != id_token_sub or core_identity_payload["sub"] != userinfo["sub"]:
                logger.error(f"Sub mismatch: core_identity sub: {core_identity_payload['sub']}, id_token sub: {id_token_sub}, userinfo sub: {userinfo['sub']}")
                raise Exception("coreIdentityJWTValidationFailed: unexpected 'sub' claim value")
            if core_identity_payload["aud"] != config.CLIENT_ID:
                logger.error(f"Audience mismatch: expected {config.CLIENT_ID}, got {core_identity_payload['aud']}")
                raise Exception("coreIdentityJWTValidationFailed: unexpected 'aud' claim value")
            if vtr_to_check and core_identity_payload["vot"] != vtr_to_check:
                error_msg = f"coreIdentityJWTValidationFailed: unexpected 'vot' claim value {core_identity_payload['vot']}, expected {vtr_to_check}"
                if return_code_value:
                    error_msg += f", returnCode value was {json.dumps(return_code_value)}"
                logger.error(error_msg)
                raise Exception(error_msg)

        session["user"] = {
            "sub": id_token_sub,
            "id_token": id_token_claims,
            "access_token": jwt.decode(access_token, options={"verify_signature": False, "verify_aud": False}),
            "userinfo": userinfo,
            "core_identity": core_identity_payload,
            "return_code": return_code_value
        }

        return redirect(url_for("verify"))

    except Exception as e:
        logger.error(f"Error in callback: {e}")
        return str(e), 500

@app.route("/home")
def home():
    return "Welcome home!"

@app.route("/verify")
def verify():
    user = session.get("user", {})
    return render_template("verify.html",
                           userinfo=user.get("userinfo", {}),
                           core_identity=user.get("core_identity", None),
                           return_code=user.get("return_code", None))

if __name__ == "__main__":
    app.run(debug=True, port=5000)