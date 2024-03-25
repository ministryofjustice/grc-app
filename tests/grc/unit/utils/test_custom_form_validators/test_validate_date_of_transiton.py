import pytest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import session
from grc.personal_details.forms import TransitionDateForm
from grc.utils.form_custom_validators import validate_date_of_transiton
from wtforms.validators import ValidationError
from unittest.mock import patch, MagicMock


class TestValidateTransitionDate:

    def test_validate_transition_date_invalid_month(self, app):
        with app.app_context():
            form = TransitionDateForm()
            form.transition_date_month.errors = ['Enter a valid month']
            form.transition_date_year.data = '2023'
            assert validate_date_of_transiton(form, form.transition_date_year) is None

    def test_validate_transition_date_invalid_date_input(self, app):
        with app.app_context():
            form = TransitionDateForm()
            form.transition_date_month.data = '12'
            form.transition_date_year.data = 'ABCSSD'
            with pytest.raises(ValidationError, match='Enter a valid year'):
                validate_date_of_transiton(form, form.transition_date_year)

    def test_validate_transition_date_invalid_date_before_earliest_possible_year(self, app):
        with app.app_context():
            form = TransitionDateForm()
            form.transition_date_month.data = '4'
            form.transition_date_year.data = '1900'
            with pytest.raises(ValidationError, match='Enter a date within the last 100 years'):
                validate_date_of_transiton(form, form.transition_date_year)

    def test_validate_transition_date_invalid_date_in_future(self, app):
        with app.app_context():
            future_date = datetime.now() + relativedelta(months=1)
            form = TransitionDateForm()
            form.transition_date_month.data = f'{future_date.month}'
            form.transition_date_year.data = f'{future_date.year}'
            with pytest.raises(ValidationError, match='Enter a date in the past'):
                validate_date_of_transiton(form, form.transition_date_year)

    @patch('grc.models.db.session')
    @patch('grc.business_logic.data_store.DataStore.load_application')
    def test_validate_transition_date_invalid_date_within_2_years_of_starting_application(self, mock_load_application,
                                                                                          mock_db_session, app):
        with app.app_context():
            with app.test_request_context():
                session['reference_number'] = '123ABC'

                test_application_created_date = datetime.now() - timedelta(days=2)
                mock_application_record = MagicMock(created=MagicMock(
                    day=test_application_created_date.day,
                    month=test_application_created_date.month,
                    year=test_application_created_date.year
                ))
                mock_application_data = MagicMock(confirmation_data=MagicMock(gender_recognition_outside_uk=False))
                mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_application_record
                mock_load_application.return_value = mock_application_data

                test_transition_date = datetime.now() - relativedelta(years=1)
                form = TransitionDateForm()
                form.transition_date_month.data = '1'
                form.transition_date_year.data = f'{test_transition_date.year}'
                with pytest.raises(ValidationError, match='Enter a date at least 2 years before your application'):
                    validate_date_of_transiton(form, form.transition_date_year)

    @patch('grc.models.db.session')
    @patch('grc.business_logic.data_store.DataStore.load_application')
    def test_validate_transition_date_valid_date_within_2_years_of_starting_application_and_transition_outside_uk(
            self, mock_load_application, mock_db_session, app):
        with app.app_context():
            with app.test_request_context():
                session['reference_number'] = '123ABC'

                test_application_created_date = datetime.now() - timedelta(days=2)
                mock_application_record = MagicMock(created=MagicMock(
                    day=test_application_created_date.day,
                    month=test_application_created_date.month,
                    year=test_application_created_date.year
                ))
                mock_application_data = MagicMock(confirmation_data=MagicMock(gender_recognition_outside_uk=True))
                mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_application_record
                mock_load_application.return_value = mock_application_data

                test_transition_date = datetime.now() - relativedelta(years=1)
                form = TransitionDateForm()
                form.transition_date_month.data = '1'
                form.transition_date_year.data = f'{test_transition_date.year}'
                assert validate_date_of_transiton(form, form.transition_date_year) is None

    @patch('grc.models.db.session')
    @patch('grc.business_logic.data_store.DataStore.load_application')
    def test_validate_transition_date_valid_date_before_2_years_of_starting_application_and_transition_inside_uk(
            self, mock_load_application, mock_db_session, app):
        with app.app_context():
            with app.test_request_context():
                session['reference_number'] = '123ABC'

                test_application_created_date = datetime.now() - timedelta(days=2)
                mock_application_record = MagicMock(created=MagicMock(
                    day=test_application_created_date.day,
                    month=test_application_created_date.month,
                    year=test_application_created_date.year
                ))
                mock_application_data = MagicMock(confirmation_data=MagicMock(gender_recognition_outside_uk=False))
                mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_application_record
                mock_load_application.return_value = mock_application_data

                test_transition_date = datetime.now() - relativedelta(years=3)
                form = TransitionDateForm()
                form.transition_date_month.data = '1'
                form.transition_date_year.data = f'{test_transition_date.year}'
                assert validate_date_of_transiton(form, form.transition_date_year) is None

    @patch('grc.models.db.session')
    @patch('grc.business_logic.data_store.DataStore.load_application')
    def test_validate_transition_date_valid_date_before_2_years_of_starting_application_and_transition_outside_uk(
            self, mock_load_application, mock_db_session, app):
        with app.app_context():
            with app.test_request_context():
                session['reference_number'] = '123ABC'

                test_application_created_date = datetime.now() - timedelta(days=2)
                mock_application_record = MagicMock(created=MagicMock(
                    day=test_application_created_date.day,
                    month=test_application_created_date.month,
                    year=test_application_created_date.year
                ))
                mock_application_data = MagicMock(confirmation_data=MagicMock(gender_recognition_outside_uk=True))
                mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_application_record
                mock_load_application.return_value = mock_application_data

                test_transition_date = datetime.now() - relativedelta(years=3)
                form = TransitionDateForm()
                form.transition_date_month.data = '1'
                form.transition_date_year.data = f'{test_transition_date.year}'
                assert validate_date_of_transiton(form, form.transition_date_year) is None
