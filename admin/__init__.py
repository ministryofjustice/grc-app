import json
import os
from admin.config import Config, TestConfig
from datetime import timedelta
from flask import Flask, g, session
from flask_babel import Babel
from flask_migrate import Migrate
from flask_uuid import FlaskUUID
from grc.models import db
from grc.utils import filters, limiter
from grc.utils.http_basic_authentication import HttpBasicAuthentication
from grc.utils.custom_error_handlers import CustomErrorHandlers
from werkzeug.middleware.proxy_fix import ProxyFix

migrate = Migrate()
flask_uuid = FlaskUUID()


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    # Require HTTP Basic Authentication if both the username and password are set
    if app.config['BASIC_AUTH_USERNAME'] and app.config['BASIC_AUTH_PASSWORD']:
        HttpBasicAuthentication(app)

    if os.environ['FLASK_ENV'] != 'development' and os.environ['FLASK_ENV'] != 'local' and os.environ['FLASK_ENV'] != 'test':
        app.config['PROPAGATE_EXCEPTIONS'] = True
        CustomErrorHandlers(app)

    # Load build info from JSON file
    f = open('build-info.json')
    build_info_string = f.read()
    f.close()
    build_info = json.loads(build_info_string)

    # database
    db.init_app(app)
    migrate.init_app(app, db)

    flask_uuid.init_app(app)

    # update session timeout time
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
                                                        "form-action 'self'"
        response.headers['Cache-Control'] = 'no-cache, no-store'
        response.headers['Expires'] = '-1'

        return response

    # Wrap app wsgi with proxy fix to reliably get user address without ip spoofing via headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    # Rate limiter
    rate_limiter = limiter.limiter(app)

    # Filters
    app.register_blueprint(filters.blueprint)

    # Admin page
    from admin.admin import admin
    if rate_limiter:
        rate_limiter.limit('5 per minute')(admin)
    app.register_blueprint(admin)

    # Signout
    from admin.signout import signout
    app.register_blueprint(signout)

    # Password reset
    from admin.password_reset import password_reset
    if rate_limiter:
        rate_limiter.limit('5 per minute')(password_reset)
    app.register_blueprint(password_reset)

    # Forgot password
    from admin.forgot_password import forgot_password
    app.register_blueprint(forgot_password)

    # Applications
    from admin.applications import applications
    app.register_blueprint(applications)

    # Manage users
    from admin.users import users
    app.register_blueprint(users)

    # System jobs
    from admin.jobs import jobs
    app.register_blueprint(jobs)

    # Tools
    from admin.tools import tools
    app.register_blueprint(tools)

    # Tech Diagnostic pages
    from admin.diagnostics import diagnostics
    app.register_blueprint(diagnostics)

    # Health Check
    from admin.health_check import health_check
    if rate_limiter:
        rate_limiter.exempt(health_check)
    app.register_blueprint(health_check)

    # GLiMR
    from admin.glimr import glimr
    app.register_blueprint(glimr)

    # Mock API for testing
    from grc.glimr_mock_api import glimr_mock_api
    if app.config.get('ENVIRONMENT', 'development') in ['development', 'local', 'test']:
        app.register_blueprint(glimr_mock_api)
        app.logger.info('GLiMR Mock API registered in admin app with routes:')
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('glimr_mock_api'):
                app.logger.info(f"  {rule.rule} [{','.join(rule.methods)}]")

    def get_locale():
        return session.get('lang_code', 'en')

    babel = Babel(app)
    babel.init_app(app, locale_selector=get_locale)

    return app
