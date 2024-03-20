from grc.models import db, SecurityCode
from grc.utils import security_code as sc


class TestSecurityCode:

    def test_delete_all_user_codes(self, app, client, security_code):
        with app.app_context():
            user_code = SecurityCode.query.filter_by(email=app.config['TEST_PUBLIC_USER'],
                                                     code=security_code.code).first()
            assert user_code is not None
            sc.delete_all_user_codes(app.config['TEST_PUBLIC_USER'])
            user_code = SecurityCode.query.filter_by(email=app.config['TEST_PUBLIC_USER'],
                                                     code=security_code.code).first()
            assert user_code is None

    def test_security_code_generator(self, app, client):
        with app.app_context():
            code = sc.security_code_generator(app.config['TEST_PUBLIC_USER'])
            user_security_code = SecurityCode.query.filter_by(email=app.config['TEST_PUBLIC_USER'], code=code).first()
            assert user_security_code is not None
            assert user_security_code.email == 'test.email@example.com'
            assert user_security_code.code == code
            db.session.delete(user_security_code)
            db.session.commit()
