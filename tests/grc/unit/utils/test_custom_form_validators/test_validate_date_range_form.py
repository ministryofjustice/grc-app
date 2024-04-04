from grc.personal_details.forms import DateRangeForm
from grc.utils.form_custom_validators import validate_date_range_form


class TestValidateDateRangeForm:

    def test_validate_date_range_form_valid_date_range(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.from_date_day.data = '1'
            form.from_date_month.data = '1'
            form.from_date_year.data = '2024'
            form.to_date_day.data = '2'
            form.to_date_month.data = '2'
            form.to_date_year.data = '2024'
            assert validate_date_range_form(form) == {}

    def test_validate_date_range_form_no_from_date_and_to_date_valid(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.to_date_day.data = '1'
            form.to_date_month.data = '1'
            form.to_date_year.data = '2024'
            expected_errors = {
                'from_date_day': 'Enter a day',
                'from_date_month': 'Enter a month',
                'from_date_year': 'Enter a year',
            }
            assert validate_date_range_form(form) == expected_errors

    def test_validate_date_range_form_no_to_date_and_from_date_valid(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.from_date_day.data = '1'
            form.from_date_month.data = '1'
            form.from_date_year.data = '2024'
            expected_errors = {
                'to_date_day': 'Enter a day',
                'to_date_month': 'Enter a month',
                'to_date_year': 'Enter a year',
            }
            assert validate_date_range_form(form) == expected_errors

    def test_validate_date_range_form_mixture_missing_date_input(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.from_date_day.data = None
            form.from_date_month.data = None
            form.from_date_year.data = '2024'
            form.to_date_day.data = None
            form.to_date_month.data = '1'
            form.to_date_year.data = None
            expected_errors = {
                'from_date_day': 'Enter a day',
                'from_date_month': 'Enter a month',
                'to_date_day': 'Enter a day',
                'to_date_year': 'Enter a year',
            }
            assert validate_date_range_form(form) == expected_errors

    def test_validate_date_range_form_from_and_to_date_input_but_from_date_invalid(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.from_date_day.data = '32'
            form.from_date_month.data = '13'
            form.from_date_year.data = '999'
            form.to_date_day.data = '1'
            form.to_date_month.data = '1'
            form.to_date_year.data = '2024'
            expected_errors = {
                'from_date_day': 'Enter a day as a number between 1 and 31',
                'from_date_month': 'Enter a month as a number between 1 and 12',
                'from_date_year': 'Enter a year as a 4-digit number, like 2000',
            }
            assert validate_date_range_form(form) == expected_errors

    def test_validate_date_range_form_from_and_to_date_input_but_to_date_invalid(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.from_date_day.data = '1'
            form.from_date_month.data = '1'
            form.from_date_year.data = '2024'
            form.to_date_day.data = '32'
            form.to_date_month.data = '13'
            form.to_date_year.data = '999'
            expected_errors = {
                'to_date_day': 'Enter a day as a number between 1 and 31',
                'to_date_month': 'Enter a month as a number between 1 and 12',
                'to_date_year': 'Enter a year as a 4-digit number, like 2000',
            }
            assert validate_date_range_form(form) == expected_errors

    def test_validate_date_range_form_mixture_invalid_date_input(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.from_date_day.data = '24'
            form.from_date_month.data = '842'
            form.from_date_year.data = '2024'
            form.to_date_day.data = '89'
            form.to_date_month.data = '7'
            form.to_date_year.data = '123'
            expected_errors = {
                'from_date_month': 'Enter a month as a number between 1 and 12',
                'to_date_day': 'Enter a day as a number between 1 and 31',
                'to_date_year': 'Enter a year as a 4-digit number, like 2000',
            }
            assert validate_date_range_form(form) == expected_errors

    def test_validate_date_range_form_mixture_missing_input_and_invalid_date_input(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.from_date_day.data = None
            form.from_date_month.data = '842'
            form.from_date_year.data = None
            form.to_date_day.data = '89'
            form.to_date_month.data = None
            form.to_date_year.data = '123'
            expected_errors = {
                'from_date_day': 'Enter a day',
                'from_date_month': 'Enter a month as a number between 1 and 12',
                'from_date_year': 'Enter a year',
                'to_date_day': 'Enter a day as a number between 1 and 31',
                'to_date_month': 'Enter a month',
                'to_date_year': 'Enter a year as a 4-digit number, like 2000',
            }
            assert validate_date_range_form(form) == expected_errors
