#!/bin/bash

#flask run --host=0.0.0.0 --port=3003
waitress-serve --call --port=3003 'jwks:create_app'