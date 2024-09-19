import pytest
from dashboard.stats.forms import DateRangeForm
from grc.utils.form_custom_validators import validate_date_range
from wtforms.validators import ValidationError


class TestValidateDateRange:
    def test_validate_date_range_invalid_start_date_day(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.start_date_day.errors = ['Enter a valid day']
            form.start_date_month.data = '1'
            form.start_date_year.data = '2023'
            form.end_date_day.data = '1'
            form.end_date_month.data = '2'
            form.end_date_year.data = '2023'
            assert validate_date_range(form, form.start_date_year) is None
            assert validate_date_range(form, form.end_date_year) is None

    def test_validate_date_range_invalid_start_date_month(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.start_date_day.data = '1'
            form.start_date_month.errors = ['Enter a valid month']
            form.start_date_year.data = '2023'
            form.end_date_day.data = '1'
            form.end_date_month.data = '2'
            form.end_date_year.data = '2023'
            assert validate_date_range(form, form.start_date_year) is None
            assert validate_date_range(form, form.end_date_year) is None

    def test_validate_date_range_invalid_end_date_day(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.start_date_day.data = '1'
            form.start_date_month.data = '1'
            form.start_date_year.data = '2023'
            form.end_date_day.errors = ['Enter a valid day']
            form.end_date_month.data = '2'
            form.end_date_year.data = '2023'
            assert validate_date_range(form, form.start_date_year) is None
            assert validate_date_range(form, form.end_date_year) is None

    def test_validate_date_range_invalid_end_date_month(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.start_date_day.data = '1'
            form.start_date_month.data = '1'
            form.start_date_year.data = '2023'
            form.end_date_day.data = '1'
            form.end_date_month.errors = ['Enter a valid month']
            form.end_date_year.data = '2023'
            assert validate_date_range(form, form.start_date_year) is None
            assert validate_date_range(form, form.end_date_year) is None

    def test_validate_date_range_invalid_start_date_year(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.start_date_day.data = '1'
            form.start_date_month.data = '1'
            form.start_date_year.data = 'INVALID YEAR'
            form.end_date_day.data = '1'
            form.end_date_month.data = '2'
            form.end_date_year.data = '2023'
            with app.test_request_context():
                with pytest.raises(ValidationError, match='Enter a valid start date'):
                    validate_date_range(form, form.start_date_year)
                    validate_date_range(form, form.end_date_year)

    def test_validate_date_range_invalid_end_date_year(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.start_date_day.data = '1'
            form.start_date_month.data = '1'
            form.start_date_year.data = '2023'
            form.end_date_day.data = '1'
            form.end_date_month.data = '2'
            form.end_date_year.data = 'INVALID YEAR'
            with app.test_request_context():
                with pytest.raises(ValidationError, match='Enter a valid end date'):
                    validate_date_range(form, form.end_date_year)
                    validate_date_range(form, form.start_date_year)

    def test_validate_date_range_start_date_greater_than_end_date(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.start_date_day.data = '15'
            form.start_date_month.data = '3'
            form.start_date_year.data = '2023'
            form.end_date_day.data = '1'
            form.end_date_month.data = '3'
            form.end_date_year.data = '2023'

            with app.test_request_context():
                with pytest.raises(ValidationError, match='The start date must be earlier than the end date'):
                    validate_date_range(form, form.start_date_year)

    def test_validate_date_range_invalid_within_range(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.start_date_day.data = '31'
            form.start_date_month.data = '2'
            form.start_date_year.data = '2023'
            form.end_date_day.data = '1'
            form.end_date_month.data = '3'
            form.end_date_year.data = '2023'

            with app.test_request_context():
                with pytest.raises(ValidationError, match='Please enter a valid start date: day is out of range for month'):
                    validate_date_range(form, form.start_date_year)

    def test_validate_date_range_end_date_greater_than_today(self, app):
        with app.app_context():
            form = DateRangeForm()
            form.start_date_day.data = '1'
            form.start_date_month.data = '1'
            form.start_date_year.data = '2023'
            form.end_date_day.data = '1'
            form.end_date_month.data = '3'
            form.end_date_year.data = '2030'

            with app.test_request_context():
                with pytest.raises(ValidationError, match='The end date cannot be in the future'):
                    validate_date_range(form, form.start_date_year)
