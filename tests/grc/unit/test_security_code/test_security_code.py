from grc.models import db, SecurityCode
from grc.utils import security_code as sc


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

    def test_is_security_code_valid_invalid_code_public_user(self, app, client, public_user_email):
        with app.app_context():
            assert sc.is_security_code_valid(public_user_email, 'INVALID CODE', False) is False
