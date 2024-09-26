import pytest
from grc.models import db, Application, ApplicationStatus, ApplicationData
from unittest.mock import patch, MagicMock


@pytest.mark.parametrize('test_emails', [3], indirect=True)
@patch('grc.utils.application_files.ApplicationFiles.delete_application_files')
def test_anonymise_expired_applications_returns_200(
        mock_delete_application_files: MagicMock, app, test_started_and_expired_applications, test_emails,
        test_completed_applications, expired_security_codes
):
    with app.app_context():
        runner = app.test_cli_runner()
        result = runner.invoke(args=['jobs.anonymise_expired_applications', 'run'])
        print(result.output)
        assert result.exit_code == 0


@patch('grc.utils.application_files.ApplicationFiles.delete_application_files')
def test_anonymise_expired_applications_abandon_application_after_period_of_inactivity(
        mock_delete_application_files: MagicMock, app, public_user_email, test_started_and_expired_applications
):
    with app.app_context():
        test_app_references = [application.reference_number for application in test_started_and_expired_applications]

        runner = app.test_cli_runner()
        result = runner.invoke(args=['jobs.anonymise_expired_applications', 'run'])
        assert result.exit_code == 0

        inactivated_applications_after_job = db.session.query(Application).filter(
            Application.reference_number.in_(test_app_references)).all()
        assert len(inactivated_applications_after_job) == 3
        for application in inactivated_applications_after_job:
            assert application.status == ApplicationStatus.ABANDONED
            assert application.email == ''
            assert application.user_input == ''

        for call in mock_delete_application_files.call_args_list:
            assert call.args[0] in test_app_references
            assert isinstance(call.args[1], ApplicationData)


@patch('grc.utils.application_files.ApplicationFiles.delete_application_files')
def test_anonymise_expired_invalid_app_data_still_abandons_applications_but_does_not_delete_data(
        mock_delete_application_files: MagicMock, app, test_started_and_expired_applications, public_user_email
):
    with app.app_context():
        test_app_references = [application.reference_number for application in test_started_and_expired_applications]
        app_with_invalid_data_ref_number = test_started_and_expired_applications[0].reference_number

        app_record: Application = Application.query.filter_by(
            reference_number=app_with_invalid_data_ref_number
        ).first()
        app_record.user_input = "{'invalid': 'json_data'}"
        db.session.commit()

        runner = app.test_cli_runner()
        result = runner.invoke(args=['jobs.anonymise_expired_applications', 'run'])
        assert result.exit_code == 0

        inactivated_applications_after_job = db.session.query(Application).filter(
            Application.reference_number.in_(test_app_references)).all()

        for application in inactivated_applications_after_job:
            if app_with_invalid_data_ref_number == application.reference_number:
                assert application.email == public_user_email
                assert application.user_input == "{'invalid': 'json_data'}"
            else:
                assert application.email == ''
                assert application.user_input == ''
            assert application.status == ApplicationStatus.ABANDONED

        for call in mock_delete_application_files.call_args_list:
            if app_with_invalid_data_ref_number == call.args[0]:
                assert call.args[1] is None
            else:
                assert isinstance(call.args[1], ApplicationData)
            assert call.args[0] in test_app_references
