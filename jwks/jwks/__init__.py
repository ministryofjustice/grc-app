import json
from flask import Blueprint, jsonify
from grc.utils.logger import LogLevel, Logger

jwks = Blueprint('jwks', __name__)
logger = Logger()


@jwks.route('/.well-known/jwks.json', methods=['GET'])
def index():
    jwks_object = {
      "keys": [
        {
            "kty": "RSA",
            "e": "AQAB",
            "use": "sig",
            "kid": "f58a6bef-0d22-444b-b4d3-507a54e9892f",
            "n": "qdxq6P7JvECWPI9b109T-l-O7-ThVfKwUKrsKlsfMTO8JEGYBgh0uoPQOVP_2BiGbjxs8M9A8z8Yn682cv6c46ZO_ArWzqKIDDOhP2GVMoUGqN8BPvKQNPsJYOBjFQA98eJilztwMpFgALViVp6v5-I54zJ-5xajfpzCuLT6MSubm-JaR1x1TWHmi82U6-deb7Y4iBoOqms3Pi8BvOP1xB5ykcgVhrMgMLGT9wMIJYEEHUUzkaQpSlkpPKEytgY3Yz-EzX5I--vreQFNMAXtT19VcijVCjJNqE-ETTzT8NWBuG0W6j7gG7w4-YyseSEIh-bHbSqzHi-s4AhYVPtbow",
        }
      ]
    }
    return jsonify(jwks_object), 200