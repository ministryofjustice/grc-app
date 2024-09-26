import pytest
from datetime import date
from dateutil.relativedelta import relativedelta
from grc.birth_registration.forms import DobForm
from grc.utils.form_custom_validators import validate_date_of_birth
from unittest.mock import patch, MagicMock
from wtforms.validators import ValidationError


class TestValidateDateOfBirth:

    @patch('grc.business_logic.data_store.DataStore.load_application')
    def test_validate_date_of_birth_after_transition_date(self, mock_load_application, app, client):
        with app.app_context():
            form = DobForm()
            form.year = None
            form['day'].data = '1'
            form['month'].data = '1'
            form['year'].data = '1990'
            form['day'].errors = None
            form['month'].errors = None

            with app.test_request_context():
                mock_data = MagicMock(personal_details_data=MagicMock(
                    transition_date=date(day=1, month=1, year=1985),
                ))
                mock_load_application.return_value = mock_data

                with pytest.raises(ValidationError, match='Your date of birth must be before your transition'
                                                          + ' date and statutory declaration date'):
                    validate_date_of_birth(form, form.year)

    @patch('grc.business_logic.data_store.DataStore.load_application')
    def test_validate_date_of_birth_after_statutory_declaration_date_valid_transition_date(self, mock_load_application,
                                                                                           app, client):
        with app.app_context():
            form = DobForm()
            form.year = None
            form['day'].data = '1'
            form['month'].data = '1'
            form['year'].data = '1990'
            form['day'].errors = None
            form['month'].errors = None

            with app.test_request_context():
                mock_data = MagicMock(personal_details_data=MagicMock(
                    transition_date=date(day=1, month=1, year=2010),
                    statutory_declaration_date=date(day=1, month=1, year=1985),
                ))
                mock_load_application.return_value = mock_data

                with pytest.raises(ValidationError, match='Your date of birth must be before your transition'
                                                          + ' date and statutory declaration date'):
                    validate_date_of_birth(form, form.year)

    @patch('grc.business_logic.data_store.DataStore.load_application')
    def test_validate_date_of_birth_after_statutory_declaration_date_no_transition_date(self, mock_load_application,
                                                                                        app, client):
        with app.app_context():
            response = client.get('/')
            assert response.status_code == 200

            form = DobForm()
            form.year = None
            form['day'].data = '1'
            form['month'].data = '1'
            form['year'].data = '1990'
            form['day'].errors = None
            form['month'].errors = None

            with app.test_request_context():
                mock_data = MagicMock(personal_details_data=MagicMock(
                    transition_date=None,
                    statutory_declaration_date=date(day=1, month=1, year=1985),
                ))
                mock_load_application.return_value = mock_data

                with pytest.raises(ValidationError, match='Your date of birth must be before your transition'
                                                          + ' date and statutory declaration date'):
                    validate_date_of_birth(form, form.year)

    def test_validate_date_of_birth_age_more_than_110(self, app, client):
        with app.test_request_context():
            input_age = date.today() - relativedelta(years=112)
            form = DobForm()
            form.year = None
            form['day'].data = f'{input_age.day}'
            form['month'].data = f'{input_age.month}'
            form['year'].data = f'{input_age.year}'
            form['day'].errors = None
            form['month'].errors = None

            with pytest.raises(ValidationError, match='You need to be less than 110 years old to apply'):
                validate_date_of_birth(form, form.year)

    def test_validate_date_of_birth_age_less_than_18(self, app, client):
        with app.app_context():
            response = client.get('/')
            assert response.status_code == 200

            input_age = date.today() - relativedelta(years=16)
            form = DobForm()
            form.year = None
            form['day'].data = f'{input_age.day}'
            form['month'].data = f'{input_age.month}'
            form['year'].data = f'{input_age.year}'
            form['day'].errors = None
            form['month'].errors = None

            with pytest.raises(ValidationError, match='You need to be at least 18 years old to apply'):
                validate_date_of_birth(form, form.year)

    def test_validate_date_of_birth_return_error_invalid_input(self, app, client):
        with app.test_request_context():
            form = DobForm()
            form.year = None
            form['day'].data = 'wdsad'
            form['month'].data = '2'
            form['year'].data = '1990'
            form['day'].errors = None
            form['month'].errors = None

            with pytest.raises(ValidationError, match='Enter a valid date'):
                validate_date_of_birth(form, form.year)

    def test_validate_date_of_birth_return_none_if_empty_day_or_month(self, app, client):
        with app.app_context():
            form = DobForm()
            form.year = None
            form['day'].data = None
            form['month'].data = None
            form['year'].data = 1990
            form['day'].errors = ['Enter a day']
            form['month'].errors = ['Enter a month']

            assert validate_date_of_birth(form, form.year) is None
