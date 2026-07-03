import dashboard
from dashboard.config import TestConfig


def test_dashboard_home_page_uses_nonce_based_csp():
    dashboard_app = dashboard.create_app(TestConfig)

    with dashboard_app.test_client() as client:
        response = client.get('/')
        csp = response.headers['Content-Security-Policy']

        assert "script-src 'self' 'nonce-" in csp
        assert "script-src-elem 'self' 'nonce-" in csp
        assert "script-src-attr 'none'" in csp
        assert "https://cdn.jsdelivr.net" in csp
        assert "img-src 'self' blob: data:" in csp
        assert "font-src 'self' data:" in csp
        assert "script-src 'self' 'unsafe-inline'" not in csp
        assert "script-src-elem 'self' 'unsafe-inline'" not in csp
        # The dashboard charts (Observable Plot) inject <style> elements and inline
        # style attributes that cannot be nonced, so inline styles are permitted here
        # while script execution stays locked to nonces.
        assert "style-src 'self' 'unsafe-inline'" in csp
        assert b'<script nonce="' in response.data
