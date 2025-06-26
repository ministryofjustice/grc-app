import json
from datetime import timedelta
from flask import Flask, g
from flask_migrate import Migrate
from flask_uuid import FlaskUUID
from grc.models import db
from werkzeug.middleware.proxy_fix import ProxyFix

migrate = Migrate()
flask_uuid = FlaskUUID()


def create_app():

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Load build info from JSON file
    f = open('build-info.json')
    build_info_string = f.read()
    f.close()
    build_info = json.loads(build_info_string)

    flask_uuid.init_app(app)

    # Update session timeout time
    @app.before_request
    def make_before_request():
        app.permanent_session_lifetime = timedelta(hours=3)
        g.build_info = build_info

    @app.after_request
    def add_header(response):
        response.headers['X-Frame-Options'] = 'deny'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; " \
                                                        "script-src 'self' 'unsafe-inline'; " \
                                                        "script-src-elem 'self' 'unsafe-inline'; " \
                                                        "script-src-attr 'self' 'unsafe-inline'; " \
                                                        "style-src 'self' 'unsafe-inline'; " \
                                                        "img-src 'self'; " \
                                                        "font-src 'self'; " \
                                                        "connect-src 'self'; " \
                                                        "form-action 'self'; "

        return response

    # Wrap app wsgi with proxy fix to reliably get user address without ip spoofing via headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    from jwks.jwks import jwks
    app.register_blueprint(jwks)

    return app
