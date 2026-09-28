from grc import create_app
from grc.config import Config


def test_home_page():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    flask_app = create_app(Config)

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200
        assert b"Apply for a Gender Recognition Certificate" in response.data


def test_home_page_uses_nonce_based_script_csp():
    flask_app = create_app(Config)

    with flask_app.test_client() as test_client:
        response = test_client.get('/')
        csp = response.headers['Content-Security-Policy']

        assert "script-src 'self' 'nonce-" in csp
        assert "script-src-elem 'self' 'nonce-" in csp
        assert "script-src-attr 'none'" in csp
        assert "style-src 'self'" in csp
        assert "script-src 'self' 'unsafe-inline'" not in csp
        assert "script-src-elem 'self' 'unsafe-inline'" not in csp
        assert "style-src 'self' 'unsafe-inline'" not in csp
        assert b'<script nonce="' in response.data
