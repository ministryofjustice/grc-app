import json
from datetime import timedelta
from flask import Flask, g, session
from flask_session import Session
from flask_babel import Babel
from flask_migrate import Migrate
from flask_uuid import FlaskUUID
from grc.models import db
from grc.utils import filters, limiter
from grc.config import Config, TestConfig
from grc.utils.http_basic_authentication import HttpBasicAuthentication
from grc.utils.maintenance_mode import Maintenance
from grc.utils.custom_error_handlers import CustomErrorHandlers
from werkzeug.middleware.proxy_fix import ProxyFix
import redis

migrate = Migrate()
flask_uuid = FlaskUUID()


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    if app.config['ENVIRONMENT'] not in app.config['NON_LIVE_ENV']:
        app.config['PROPAGATE_EXCEPTIONS'] = True
        CustomErrorHandlers(app)

    # Show "Service unavailable" page if the config setting it set
    if app.config['MAINTENANCE_MODE'] == 'ON':
        Maintenance(app)
        return app

    # Require HTTP Basic Authentication if both the username and password are set
    if app.config['BASIC_AUTH_USERNAME'] and app.config['BASIC_AUTH_PASSWORD']:
        HttpBasicAuthentication(app)

    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = redis.Redis(host="grc_redis", port=6379, db=0)
    Session(app)

    # Load build info from JSON file
    f = open('build-info.json')
    build_info_string = f.read()
    f.close()
    build_info = json.loads(build_info_string)

    # Database
    db.init_app(app)
    migrate.init_app(app, db)

    flask_uuid.init_app(app)

    # Update session timeout time
    @app.before_request
    def make_before_request():
        app.permanent_session_lifetime = timedelta(hours=3)
        g.build_info = build_info
        g.lang_code = get_locale()

    @app.after_request
    def add_header(response):
        response.headers['X-Frame-Options'] = 'deny'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; " \
                                                        "script-src 'self' 'unsafe-inline' https://*.googletagmanager.com https://*.google-analytics.com; " \
                                                        "script-src-elem 'self' 'unsafe-inline' https://*.googletagmanager.com https://*.google-analytics.com; " \
                                                        "script-src-attr 'self' 'unsafe-inline'; " \
                                                        "style-src 'self' 'unsafe-inline'; " \
                                                        "img-src 'self'; " \
                                                        "font-src 'self'; " \
                                                        "connect-src 'self' https://*.google-analytics.com; " \
                                                        "form-action 'self' https://card.payments.service.gov.uk https://oidc.integration.account.gov.uk/ https://signin.integration.account.gov.uk/ https://identity.integration.account.gov.uk/; "

        return response

    # Wrap app wsgi with proxy fix to reliably get user address without ip spoofing via headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    # Rate limiter
    rate_limiter = limiter.limiter(app)

    # Filters
    app.register_blueprint(filters.blueprint)

    # Homepage
    from grc.start_application import startApplication
    if rate_limiter:
        rate_limiter.limit('5 per minute')(startApplication)
    app.register_blueprint(startApplication)

    # Save And Return
    from grc.save_and_return import saveAndReturn
    app.register_blueprint(saveAndReturn)

    # Task List
    from grc.task_list import taskList
    app.register_blueprint(taskList)

    # Personal details
    from grc.personal_details import personalDetails
    app.register_blueprint(personalDetails)

    # Birth registration
    from grc.birth_registration import birthRegistration
    app.register_blueprint(birthRegistration)

    # Partnership details
    from grc.partnership_details import partnershipDetails
    app.register_blueprint(partnershipDetails)

    # Upload
    from grc.upload import upload
    if rate_limiter:
        rate_limiter.exempt(upload)
    app.register_blueprint(upload)

    # Submit and pay
    from grc.submit_and_pay import submitAndPay
    app.register_blueprint(submitAndPay)

    # Policies
    from grc.policies import policies
    app.register_blueprint(policies)

    # Feedback
    from grc.feedback import feedback
    app.register_blueprint(feedback)

    # Document checker
    from grc.document_checker import documentChecker
    app.register_blueprint(documentChecker)

    # Document checker
    from grc.one_login import oneLogin
    app.register_blueprint(oneLogin)

    # Health Check
    from grc.health_check import health_check
    if rate_limiter:
        rate_limiter.exempt(health_check)
    app.register_blueprint(health_check)

    # Set langauge
    from .language import set_language
    app.register_blueprint(set_language)

    def get_locale():
        return session.get('lang_code', 'en')

    babel = Babel(app)
    babel.init_app(app, locale_selector=get_locale)

    return app
