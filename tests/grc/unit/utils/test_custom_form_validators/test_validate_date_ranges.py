from datetime import date
from dateutil.relativedelta import relativedelta
from grc.utils.form_custom_validators import validate_date_ranges


class TestValidateDateRanges:

    def test_validate_date_ranges_valid_date_range(self, app):
        with app.test_request_context():
            test_from_date = date.today()
            test_to_date = date.today() + relativedelta(months=1)
            assert validate_date_ranges(test_from_date, test_to_date) == {}

    def test_validate_date_ranges_invalid_from_date_in_past(self, app):
        with app.test_request_context():
            test_from_date = date.today() - relativedelta(days=1)
            test_to_date = date.today() + relativedelta(months=1)
            expected_errors = {'from_date_year': "'From' date is in the past"}
            assert validate_date_ranges(test_from_date, test_to_date) == expected_errors

    def test_validate_date_ranges_invalid_to_date_in_past(self, app):
        with app.test_request_context():
            test_from_date = date.today() - relativedelta(months=2)
            test_to_date = date.today() - relativedelta(months=1)
            assert validate_date_ranges(test_from_date, test_to_date)['to_date_year'] == "'To' date is in the past"

    def test_validate_date_ranges_invalid_both_dates_in_past(self, app):
        with app.test_request_context():
            test_from_date = date.today() - relativedelta(months=2)
            test_to_date = date.today() - relativedelta(months=1)
            expected_errors = {
                'from_date_year': "'From' date is in the past",
                'to_date_year': "'To' date is in the past"
            }
            assert validate_date_ranges(test_from_date, test_to_date) == expected_errors

    def test_validate_date_ranges_invalid_to_date_before_from_date(self, app):
        with app.test_request_context():
            test_from_date = date.today() + relativedelta(months=2)
            test_to_date = date.today() + relativedelta(months=1)
            expected_errors = {'to_date_year': "'From' date is after the 'To' date"}
            assert validate_date_ranges(test_from_date, test_to_date) == expected_errors

    def test_validate_date_ranges_invalid_both_dates_in_past_and_to_date_before_from_date(self, app):
        with app.test_request_context():
            test_from_date = date.today() - relativedelta(months=1)
            test_to_date = date.today() - relativedelta(months=2)
            expected_errors = {
                'from_date_year': "'From' date is in the past",
                'to_date_year': "'From' date is after the 'To' date"
            }
            assert validate_date_ranges(test_from_date, test_to_date) == expected_errors
