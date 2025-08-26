from flask import Blueprint, jsonify
from grc.utils.logger import LogLevel, Logger
from typing import Any
from flask import current_app
import json

jwks = Blueprint('jwks', __name__)
logger = Logger()


@jwks.route('/.well-known/jwks.json', methods=['GET'])
def index():
    public_key = load_public_key_jwk()

    jwks_object = {
      "keys": [
        public_key,
      ]
    }

    return jsonify(jwks_object), 200

def load_public_key_jwk() -> dict[str, Any]:
    try:
        public_key_path = current_app.config.get('ONE_LOGIN_PUBLIC_KEY_PATH')

        if not public_key_path:
            logger.log(LogLevel.ERROR, 'Cannot find public key file')
            return {}

        with open(public_key_path, "rb") as f:
            jwk = json.load(f)
            return jwk

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return {}
