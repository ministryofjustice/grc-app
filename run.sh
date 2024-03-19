#!/bin/bash

echo "flask db commands commented out to bypass db migration"
#flask db init
#flask db migrate
#flask db upgrade
#flask run --host=0.0.0.0 -p 3000

waitress-serve --call --port=3000 'grc:create_app'