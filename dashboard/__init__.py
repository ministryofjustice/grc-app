import json
from datetime import timedelta
from flask import Flask, g, session
from flask_babel import Babel
from flask_migrate import Migrate
from flask_uuid import FlaskUUID
from grc.models import db
from grc.utils import filters, limiter
from dashboard.config import Config
from grc.utils.csp import build_csp, csp_context, generate_nonce
from grc.utils.http_basic_authentication import HttpBasicAuthentication
from grc.utils.http_ip_whitelist import HttpIPWhitelist
from grc.utils.custom_error_handlers import CustomErrorHandlers
from health.health_check import HealthCheckBase


migrate = Migrate()
flask_uuid = FlaskUUID()


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config:
        app.config.from_object(test_config)
    else:
        app.config.from_object(Config)

    if app.config['IP_WHITELIST']:
        HttpIPWhitelist(app)

    # Require HTTP Basic Authentication if both the username and password are set
    if app.config['BASIC_AUTH_USERNAME'] and app.config['BASIC_AUTH_PASSWORD']:
        HttpBasicAuthentication(app)

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
    app.context_processor(csp_context)

    # update session timeout time
    @app.before_request
    def make_before_request():
        app.permanent_session_lifetime = timedelta(hours=3)
        g.build_info = build_info
        generate_nonce()

    @app.after_request
    def add_header(response):
        response.headers['X-Frame-Options'] = 'deny'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = build_csp(
            script_hosts=['https://cdn.jsdelivr.net'],
            img_hosts=['blob:', 'data:'],
            font_hosts=['data:'],
            # The dashboard renders charts with Observable Plot, which injects
            # <style> elements and inline style attributes on generated SVG/figure
            # nodes that cannot be nonced. The dashboard was not an ITHC VUL-6942
            # target; script execution stays locked down via the nonce-based
            # script-src while inline styles are permitted for the charting library.
            style_hosts=["'unsafe-inline'"],
        )

        return response

    # Rate limiter
    rate_limiter = limiter.limiter(app)

    # Filters
    app.register_blueprint(filters.blueprint)

    # Dashboard page
    from dashboard.stats import stats
    if rate_limiter:
        rate_limiter.limit('5 per minute')(stats)
    app.register_blueprint(stats)

    # Feedback page
    from dashboard.feedback import feedback
    app.register_blueprint(feedback)

    # Health Check
    from dashboard.health_check import health_check
    if rate_limiter:
        rate_limiter.exempt(health_check)
    app.register_blueprint(health_check)

    def get_locale():
        return session.get('lang_code', 'en')

    babel = Babel(app)
    babel.init_app(app, locale_selector=get_locale)

    return app
