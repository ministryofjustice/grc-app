import pytest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import session
from grc.personal_details.forms import StatutoryDeclarationDateForm
from grc.utils.form_custom_validators import validate_statutory_declaration_date
from wtforms.validators import ValidationError
from unittest.mock import patch, MagicMock


class Testvalidate_statutory_declaration_date:

    def test_validate_statutory_declaration_date_invalid_day(self, app):
        with app.app_context():
            form = StatutoryDeclarationDateForm()
            form.statutory_declaration_date_day.errors = ['Enter a valid day']
            form.statutory_declaration_date_year.data = '2023'
            assert validate_statutory_declaration_date(form, form.statutory_declaration_date_year) is None

    def test_validate_statutory_declaration_date_invalid_month(self, app):
        with app.app_context():
            form = StatutoryDeclarationDateForm()
            form.statutory_declaration_date_month.errors = ['Enter a valid month']
            form.statutory_declaration_date_year.data = '2023'
            assert validate_statutory_declaration_date(form, form.statutory_declaration_date_year) is None

    def test_validate_statutory_declaration_date_invalid_day_and_month(self, app):
        with app.app_context():
            form = StatutoryDeclarationDateForm()
            form.statutory_declaration_date_day.errors = ['Enter a valid day']
            form.statutory_declaration_date_month.errors = ['Enter a valid month']
            form.statutory_declaration_date_year.data = '2023'
            assert validate_statutory_declaration_date(form, form.statutory_declaration_date_year) is None

    def test_validate_statutory_declaration_invalid_date_input(self, app):
        with app.app_context():
            form = StatutoryDeclarationDateForm()
            form.statutory_declaration_date_day.data = '24'
            form.statutory_declaration_date_month.data = '3'
            form.statutory_declaration_date_year.data = 'ABCSSD'
            with pytest.raises(ValidationError, match='Enter a valid year'):
                validate_statutory_declaration_date(form, form.statutory_declaration_date_year)

    def test_validate_statutory_declaration_date_invalid_date_before_earliest_possible_year(self, app):
        with app.app_context():
            form = StatutoryDeclarationDateForm()
            form.statutory_declaration_date_day.data = '4'
            form.statutory_declaration_date_month.data = '3'
            form.statutory_declaration_date_year.data = '1900'
            with pytest.raises(ValidationError, match='Enter a date within the last 100 years'):
                validate_statutory_declaration_date(form, form.statutory_declaration_date_year)

    def test_validate_statutory_declaration_date_invalid_date_in_future(self, app):
        with app.app_context():
            future_date = datetime.now() + relativedelta(months=1)
            form = StatutoryDeclarationDateForm()
            form.statutory_declaration_date_day.data = '4'
            form.statutory_declaration_date_month.data = f'{future_date.month}'
            form.statutory_declaration_date_year.data = f'{future_date.year}'
            with pytest.raises(ValidationError, match='Enter a date in the past'):
                validate_statutory_declaration_date(form, form.statutory_declaration_date_year)

    @patch('grc.business_logic.data_store.DataStore.load_application')
    def test_validate_statutory_declaration_date_invalid_date_before_transition_date(self, mock_load_application, app):
        with app.app_context():
            with app.test_request_context():
                session['reference_number'] = '123ABC'

                mock_transition_date = (datetime.today() - relativedelta(years=3)).date()
                mock_application_data = MagicMock(personal_details_data=MagicMock(transition_date=mock_transition_date))
                mock_load_application.return_value = mock_application_data

                statutory_declaration_date_year = datetime.now() - relativedelta(years=4)
                form = StatutoryDeclarationDateForm()
                form.statutory_declaration_date_day.data = '4'
                form.statutory_declaration_date_month.data = '6'
                form.statutory_declaration_date_year.data = f'{statutory_declaration_date_year.year}'
                with pytest.raises(ValidationError, match='Enter a date that does not precede your transition date'):
                    validate_statutory_declaration_date(form, form.statutory_declaration_date_year)

    @patch('grc.business_logic.data_store.DataStore.load_application')
    def test_validate_statutory_declaration_date_valid_date(self, mock_load_application, app):
        with app.app_context():
            with app.test_request_context():
                session['reference_number'] = '123ABC'

                mock_transition_date = (datetime.today() - relativedelta(years=3)).date()
                mock_application_data = MagicMock(personal_details_data=MagicMock(transition_date=mock_transition_date))
                mock_load_application.return_value = mock_application_data

                statutory_declaration_date_year = datetime.now() - relativedelta(years=2)
                form = StatutoryDeclarationDateForm()
                form.statutory_declaration_date_day.data = '4'
                form.statutory_declaration_date_month.data = '6'
                form.statutory_declaration_date_year.data = f'{statutory_declaration_date_year.year}'
                assert validate_statutory_declaration_date(form, form.statutory_declaration_date_year) is None
