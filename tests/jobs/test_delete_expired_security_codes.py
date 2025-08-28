import pytest
from grc.models import SecurityCode, db


@pytest.mark.parametrize('test_emails', [3], indirect=True)
def test_delete_expired_security_codes_returns_200(
        app, test_started_and_expired_applications, test_emails, test_completed_applications, expired_security_codes
):
    with app.app_context():
        runner = app.test_cli_runner()
        result = runner.invoke(args=['jobs.delete_expired_security_codes', 'run'])
        assert result.exit_code == 0


@pytest.mark.parametrize('test_emails', [3], indirect=True)
def test_notify_applicants_inactive_applications_deletes_expired_security_codes(app, expired_security_codes,
                                                                                test_emails):
    with app.app_context():
        runner = app.test_cli_runner()
        result = runner.invoke(args=['jobs.delete_expired_security_codes', 'run'])
        print(result.output)
        assert result.exit_code == 0

        deleted_security_codes = db.session.query(SecurityCode).filter(SecurityCode.email.in_(test_emails)).all()
        assert len(deleted_security_codes) == 0
