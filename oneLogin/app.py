from flask import Flask, redirect, url_for
from authlib.integrations.flask_client import OAuth
from authlib.jose import jwt
from flask import render_template

import logging
import sys
import json
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'
oauth = OAuth(app)

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger('authlib')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

# Load the client_secrets.json file
with open('client_secrets.json') as f:
    client_secrets = json.load(f)

# Load your private key
with open('grc-onelogin-private.pem', 'rb') as f:
    private_key = f.read()

# Define a function to sign the JWT when maaking the token request
def sign_jwt():
    header = {'alg': 'RS256'}
    payload = {
        'iss': client_secrets['web']['client_id'],
        'sub': client_secrets['web']['client_id'],
        'aud': client_secrets['web']['token_uri'],
        'iat': int(time.time()),
        'exp': int(time.time()) + 300,
        'jti': 'unique-jwt-id'
    }
    return jwt.encode(header, payload, private_key).decode('utf-8')

oauth.register(
    name='onelogin',
    client_id=client_secrets['web']['client_id'],
    client_auth_method='private_key_jwt',
    access_token_url=client_secrets['web']['token_uri'],
    authorize_url=client_secrets['web']['auth_uri'],
    client_kwargs={'scope': 'openid phone email'},
    token_endpoint_auth_method='private_key_jwt'
)

#{name}_CLIENT_ID: Client key of OAuth 1, or Client ID of OAuth 2
#{name}_CLIENT_SECRET: Client secret of OAuth 2, or Client Secret of OAuth 2
#{name}_REQUEST_TOKEN_URL: Request Token endpoint for OAuth 1
#{name}_REQUEST_TOKEN_PARAMS: Extra parameters for Request Token endpoint
#{name}_ACCESS_TOKEN_URL: Access Token endpoint for OAuth 1 and OAuth 2
#{name}_ACCESS_TOKEN_PARAMS: Extra parameters for Access Token endpoint
#{name}_AUTHORIZE_URL: Endpoint for user authorization of OAuth 1 ro OAuth 2
#{name}_AUTHORIZE_PARAMS: Extra parameters for Authorization Endpoint.
#{name}_API_BASE_URL: A base URL endpoint to make requests simple
#{name}_CLIENT_KWARGS: Extra keyword arguments for OAuth1Session or OAuth2Session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    token = sign_jwt()
    redirect_uri = url_for('authorize', _external=True)
    #response = oauth.onelogin.authorize_redirect(redirect_uri, client_assertion=token)
    response = oauth.onelogin.authorize_redirect(redirect_uri)

    # Log the redirect URL
    logging.debug(f'Redirecting to: {response.headers["Location"]}')
    return response

@app.route('/oidc/authorization-code/callback')
def authorize():
    # Retrieve the authorisation code and state

    #token = oauth.onelogin.authorize_access_token()
    #logging.debug(f'Token: {token}')
    #user_info = oauth.onelogin.parse_id_token(token)
    return f'Hello, {user_info["email"]}'

if __name__ == '__main__':
    app.run(debug=True)

