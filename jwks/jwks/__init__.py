import json
from flask import Blueprint, jsonify
from grc.utils.logger import LogLevel, Logger

jwks = Blueprint('jwks', __name__)
logger = Logger()


@jwks.route('/', methods=['GET'])
def index():
    jwks_object = {
      "keys": [
        {
          "kty": "RSA",
          "kid": "sample-key-id",
          "use": "sig",
          "alg": "RS256",
          "n": "sXchqkqU58gXGfAeF6OZB5fUIBQ1fHtLhM0Kk04RfVHgWo8yZTZwAPl4Yl6hOZk6B_AvVP6Z4HJSJdXxU_bCWmXWRLAvYfArKW5z13VmCKRrgB-mgR-9CPWv7z3sE4gINzTZlpyIRnPfXxAfMSljYKwYtHO9FZsTddXGH4TCM4RClv_Nd5Re5cT8XxwJvDJeHkXHFXITZRtTqPvPrVuPbSwFnpYhYFTuMy0LMGwqNUn8Epx3gfGgLqYGi8OaQ10YY2qxEDPKPygXi1BtjgcUhzr7JY4rglzDeU-6z_xPYkSPZniJxNVDRlUzGR-1XRxEOxEBck2hxkxNuzU3S8ey8N28w",
          "e": "AQAB"
        }
      ]
    }
    return jsonify(jwks_object)