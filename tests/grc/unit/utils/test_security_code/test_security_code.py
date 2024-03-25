from datetime import datetime, timedelta
from grc.models import db, SecurityCode
from grc.utils import security_code as sc
from unittest.mock import patch


class TestSecurityCode:

    def test_delete_all_user_codes(self, app, client, security_code_, public_user_email):
        with app.app_context():
            user_code = SecurityCode.query.filter_by(email=public_user_email,
                                                     code=security_code_.code).first()
            assert user_code is not None
            sc.delete_all_user_codes(public_user_email)
            user_code = SecurityCode.query.filter_by(email=public_user_email,
                                                     code=security_code_.code).first()
            assert user_code is None

    def test_security_code_generator(self, app, client, public_user_email):
        with app.app_context():
            code = sc.security_code_generator(public_user_email)
            user_security_code = SecurityCode.query.filter_by(email=public_user_email, code=code).first()
            assert user_security_code is not None
            assert user_security_code.email == 'test.public.email@example.com'
            assert user_security_code.code == code
            db.session.delete(user_security_code)
            db.session.commit()

    def test_is_security_code_valid_valid_code_no_user(self, app, client, public_user_email, security_code_):
        with app.app_context():
            with app.test_request_context():
                assert sc.is_security_code_valid(None, security_code_.code, False) is False

    def test_is_security_code_valid_invalid_code_public_user(self, app, client, public_user_email):
        with app.app_context():
            with app.test_request_context():
                assert sc.is_security_code_valid(public_user_email, 'INVALID CODE', False) is False

    def test_is_security_code_valid_invalid_code_admin_user(self, app, client, public_user_email):
        with app.app_context():
            with app.test_request_context():
                assert sc.is_security_code_valid(public_user_email, 'INVALID CODE', True) is False

    def test_is_security_code_valid_invalid_email_public_user(self, app, client, public_user_email, security_code_):
        with app.app_context():
            with app.test_request_context():
                assert sc.is_security_code_valid('INVALID EMAIL', security_code_.code, False) is False

    def test_is_security_code_valid_invalid_email_admin_user(self, app, client, public_user_email, security_code_):
        with app.app_context():
            with app.test_request_context():
                assert sc.is_security_code_valid('INVALID EMAIL', security_code_.code, True) is False

    def test_is_security_code_valid_expired_code_public_user(self, app, client, public_user_email,
                                                             expired_security_code):
        with app.app_context():
            with app.test_request_context():
                assert sc.is_security_code_valid(public_user_email, expired_security_code.code, False) is False

    def test_is_security_code_valid_expired_code_admin_user(self, app, client, public_user_email,
                                                            expired_security_code):
        with app.app_context():
            with app.test_request_context():
                assert sc.is_security_code_valid(public_user_email, expired_security_code.code, True) is False

    def test_is_security_code_valid_valid_code_admin_user_code_not_deleted(self, app, client, public_user_email,
                                                                           security_code_):
        with app.app_context():
            with app.test_request_context():
                assert sc.is_security_code_valid(public_user_email, security_code_.code, True) is True
                user_security_code = SecurityCode.query.filter_by(email=public_user_email,
                                                                  code=security_code_.code).first()
                assert user_security_code is not None
                assert user_security_code.code == security_code_.code
                assert user_security_code.email == 'test.public.email@example.com'

    @patch('grc.utils.security_code.delete_all_user_codes')
    def test_is_security_code_valid_valid_code_public_user_code_deleted(self, mock_delete_all_user_codes,
                                                                        app, client, public_user_email,
                                                                        security_code_):
        with app.app_context():
            with app.test_request_context():
                assert sc.is_security_code_valid(public_user_email, security_code_.code, False) is True
                mock_delete_all_user_codes.assert_called_with(public_user_email)

    @patch('grc.utils.date_utils.convert_date_to_local_timezone')
    @patch('grc.utils.security_code.security_code_generator')
    def test_generate_security_code(self, mock_security_code_generator, mock_datetime, app, client, public_user_email,
                                    security_code_):
        with (app.app_context()):
            expiry_datetime = datetime.now() + timedelta(hours=24)
            mock_datetime.return_value = expiry_datetime

            mock_security_code_generator.return_value = security_code_.code
            assert sc.generate_security_code(public_user_email) == (security_code_.code, expiry_datetime.strftime(
                '%H:%M on %d %b %Y'))

    def test_has_last_security_code_been_used_last_security_code_used(self, app):
        with app.app_context():
            last_login_date = datetime.now() - timedelta(hours=1)
            security_code_created_date = datetime.now() - timedelta(hours=23)
            assert sc.has_last_security_code_been_used(last_login_date, security_code_created_date) is True

    def test_has_last_security_code_been_used_last_security_code_not_used(self, app):
        with app.app_context():
            last_login_date = datetime.now() - timedelta(hours=10)
            security_code_created_date = datetime.now() - timedelta(hours=5)
            assert sc.has_last_security_code_been_used(last_login_date, security_code_created_date) is False

    def test_has_last_security_code_been_used_last_security_expired(self, app):
        with app.app_context():
            security_created_date = datetime.now() - timedelta(hours=5)
            assert sc.has_security_code_expired(security_created_date, datetime.now()) is True

    def test_has_last_security_code_been_used_last_security_not_expired(self, app):
        with app.app_context():
            security_created_date = datetime.now() + timedelta(hours=5)
            assert sc.has_security_code_expired(security_created_date, datetime.now()) is False
