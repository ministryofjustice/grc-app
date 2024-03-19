from grc.start_application.forms import SecurityCodeForm
from grc.utils.form_custom_validators import validate_security_code
from unittest.mock import patch


class TestValidateSecurityCode:

    def test_validate_security_code_test_or_local(self, app, client):
        with app.app_context():
            response = client.get('/')
            assert response.status_code == 200

            form = SecurityCodeForm()
            form.security_code.data = '11111'

            assert validate_security_code(form, form.security_code) is None

    @patch('grc.utils.security_code.is_security_code_valid')
    def test_validate_security_code_valid_public_user(self, mock_is_security_code_valid, app, client):
        with app.app_context():
            response = client.get('/')
            assert response.status_code == 200

            form = SecurityCodeForm()
            form.security_code.data = '12345'

            with app.test_request_context():
                mock_is_security_code_valid.return_value = True
                assert validate_security_code(form, form.security_code) is None
