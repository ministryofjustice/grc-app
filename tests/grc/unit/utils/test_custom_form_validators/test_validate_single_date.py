import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from grc.personal_details.forms import ContactDatesForm
from grc.utils.form_custom_validators import validate_single_date
from wtforms.validators import ValidationError


class TestValidateSingleDate:

    def test_validate_single_date_valid_date(self, app):
        with app.app_context():
            future_date = datetime.today() + relativedelta(months=6)
            form = ContactDatesForm()
            form.contactDatesCheck.data = 'SINGLE_DATE'
            form.day.data = '1'
            form.month.data = f'{future_date.month}'
            form.year.data = f'{future_date.year}'
            assert validate_single_date(form, form.year) is None

    def test_validate_single_date_invalid_day_error(self, app):
        with app.app_context():
            future_date = datetime.today() + relativedelta(months=6)
            form = ContactDatesForm()
            form.contactDatesCheck.data = 'SINGLE_DATE'
            form.day.errors = ['Enter a day']
            form.month.data = f'{future_date.month}'
            form.year.data = f'{future_date.year}'
            assert validate_single_date(form, form.year) is None

    def test_validate_single_date_invalid_month_error(self, app):
        with app.app_context():
            future_date = datetime.today() + relativedelta(months=6)
            form = ContactDatesForm()
            form.contactDatesCheck.data = 'SINGLE_DATE'
            form.day.data = '1'
            form.month.errors = ['Enter a month']
            form.year.data = f'{future_date.year}'
            assert validate_single_date(form, form.year) is None

    def test_validate_single_date_invalid_year_date(self, app):
        with app.app_context():
            form = ContactDatesForm()
            form.contactDatesCheck.data = 'SINGLE_DATE'
            form.day.data = '1'
            form.month.data = '1'
            form.year.data = 'INVALID YEAR'
            with pytest.raises(ValidationError, match='Enter a valid date'):
                validate_single_date(form, form.year)

    def test_validate_single_date_invalid_date_in_past(self, app):
        with app.app_context():
            past_date = datetime.today() - relativedelta(months=6)
            form = ContactDatesForm()
            form.contactDatesCheck.data = 'SINGLE_DATE'
            form.day.data = '1'
            form.month.data = f'{past_date.month}'
            form.year.data = f'{past_date.year}'
            with pytest.raises(ValidationError, match='Enter a date in the future'):
                validate_single_date(form, form.year)
