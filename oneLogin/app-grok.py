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

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Setup Flask app and OAuth
app = Flask(__name__)
app.secret_key = "your-secret-key"  # Required for session
oauth = OAuth(app)


# Configuration (replace with your actual values)
class Config:
    ISSUER = "https://oidc.integration.account.gov.uk"
    TOKEN_URI = "https://oidc.integration.account.gov.uk/token"
    CLIENT_ID = "o8bkoFoPZvyzlxGJ6SRVlhprYkM"
    PRIVATE_KEY_PATH = "grc-onelogin-private.pem"
    REDIRECT_URI = "http://localhost:5000/oidc/authorization-code/callback"
    SCOPE = "openid phone email"
    TOKEN_AUTH_METHOD = "private_key_jwt"  # or "client_secret_post or private_key_jwt"
    REQUIRE_JAR = False
    IV_ISSUER = "o8bkoFoPZvyzlxGJ6SRVlhprYkM"  # For coreIdentityJWT
    IDENTITY_VTR = "P2.Cl.Cm"  # Example Vector of Trust
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

# Verify private key
try:
    with open(config.PRIVATE_KEY_PATH, "rb") as f:
        private_key_content = f.read()
        logger.info(f"Private key loaded from {config.PRIVATE_KEY_PATH}")
except Exception as e:
    logger.error(f"Failed to load private key: {e}")
    raise

# Custom JWT assertion
def create_jwt_assertion():
    now = int(time.time())
    payload = {
        "aud": config.TOKEN_URI,
        "iss": config.CLIENT_ID,
        "sub": config.CLIENT_ID,
        "exp": now + 300,  # 5 minutes
        "jti": str(uuid.uuid4()),
        "iat": now
    }
    with open(config.PRIVATE_KEY_PATH, "rb") as f:
        private_key = f.read()
    return jwt.encode(payload, private_key, algorithm="RS256")

# Custom token fetch
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

oauth.register(
    name="oidc",
    client_id=config.CLIENT_ID,
    client_secret=None,
    server_metadata_url=f"{config.ISSUER}/.well-known/openid-configuration",
    client_kwargs={"scope": config.SCOPE},
)

# Load public key for coreIdentityJWT verification (simplified, adjust as needed)
def get_identity_signing_public_key(kid):
    # In a real app, fetch this from a JWKS endpoint or config based on kid
    with open(client.PRIVATE_KEY_PATH, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())

@app.route('/')
def index():
    return render_template('index.html')

# Authorization route (from previous example)
@app.route("/login")
def login():
    client = oauth.oidc
    nonce = "random-nonce"
    state = "random-state"
    session["nonce"] = nonce
    session["state"] = state
    result = client.authorize_redirect(
        redirect_uri=config.REDIRECT_URI,
        scope=config.SCOPE,
        response_type="code",
        state=state,
        nonce=nonce
    )
    logger.info(f"authorize_redirect result: {result}, type: {type(result)}")
    return result

# Callback route (token exchange and processing)
@app.route("/oidc/authorization-code/callback")
def callback():
    try:
        logger.info("Back in callback")
        if "error" in request.args:
            error = request.args["error"]
            desc = request.args.get("error_description", "")
            raise Exception(f"{error} - {desc}")

        client = oauth.oidc
        nonce = session.get("nonce")
        state = session.get("state")
        code = request.args.get("code")
        if not code:
            raise Exception("No code received in callback")

        token = fetch_token(code)

        id_token = token.get("id_token")
        access_token = token.get("access_token")
        id_token_claims = jwt.decode(id_token, options={"verify_signature": False})
        if id_token_claims.get("nonce") != nonce:
            raise Exception("Nonce mismatch")

        response = app.make_response("Processing complete")
        response.set_cookie("id-token", id_token, httponly=True)

        userinfo = client.fetch_user_info(access_token=access_token)
        id_token_sub = id_token_claims["sub"]

        core_identity_payload = None
        return_code_value = userinfo.get("https://vocab.account.gov.uk/v1/returnCode")

        if "https://vocab.account.gov.uk/v1/coreIdentityJWT" in userinfo:
            core_identity_jwt = userinfo["https://vocab.account.gov.uk/v1/coreIdentityJWT"]
            logger.debug(f"Core Identity JWT: {core_identity_jwt}")
            header = jwt.get_unverified_header(core_identity_jwt)
            kid = header["kid"]
            public_key = get_identity_signing_public_key(kid)
            core_identity_payload = jwt.decode(
                core_identity_jwt,
                public_key,
                algorithms=["RS256"],
                issuer=config.IV_ISSUER
            )
            vtr_to_check = config.IDENTITY_VTR.replace(r"[.Clm]", "") if config.IDENTITY_VTR else None
            if core_identity_payload["sub"] != id_token_sub or core_identity_payload["sub"] != userinfo["sub"]:
                raise Exception("coreIdentityJWTValidationFailed: unexpected 'sub' claim value")
            if core_identity_payload["aud"] != config.CLIENT_ID:
                raise Exception("coreIdentityJWTValidationFailed: unexpected 'aud' claim value")
            if vtr_to_check and core_identity_payload["vot"] != vtr_to_check:
                error_msg = f"coreIdentityJWTValidationFailed: unexpected 'vot' claim value {core_identity_payload['vot']}, expected {vtr_to_check}"
                if return_code_value:
                    error_msg += f", returnCode value was {json.dumps(return_code_value)}"
                raise Exception(error_msg)

        session["user"] = {
            "sub": id_token_sub,
            "id_token": id_token_claims,
            "access_token": jwt.decode(access_token, options={"verify_signature": False}),
            "userinfo": userinfo,
            "core_identity": core_identity_payload,
            "return_code": return_code_value
        }

        if config.IMMEDIATE_REDIRECT and config.IDENTITY_SUPPORTED and core_identity_payload is None:
            return redirect(url_for("verify"))
        return redirect(url_for("home"))

    except Exception as e:
        logger.error(f"Error in callback: {e}")
        return str(e), 500

# Placeholder routes for redirects
@app.route("/oidc/verify")
def verify():
    return "Verification page"

if __name__ == "__main__":
    app.run(debug=True, port=5000)