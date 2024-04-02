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
                with pytest.raises(ValidationError, match='Enter a valid start year'):
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
                with pytest.raises(ValidationError, match='Enter a valid end year'):
                    validate_date_range(form, form.end_date_year)
                    validate_date_range(form, form.start_date_year)
