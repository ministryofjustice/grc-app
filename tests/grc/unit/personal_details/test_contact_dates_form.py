from datetime import date
from dateutil.relativedelta import relativedelta
from grc.utils.form_custom_validators import validate_date_range_form, validate_date_ranges
from grc.personal_details.forms import ContactDatesForm, DateRangeForm
from grc.business_logic.data_structures.personal_details_data import ContactDatesAvoid
from tests.grc.helpers.data.dates import DateHelpers


class TestContactDatesForm:

    def test_contact_single_date_valid(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.SINGLE_DATE.value
            valid_date = date.today() + relativedelta(days=7)
            DateHelpers.single_date_mock(contact_dates_form, valid_date)
            assert contact_dates_form.validate()

    def test_contact_single_date_in_the_past(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.SINGLE_DATE.value
            invalid_date = date.today() - relativedelta(days=7)
            DateHelpers.single_date_mock(contact_dates_form, invalid_date)
            assert not contact_dates_form.validate()
            assert contact_dates_form.errors['year'][0] == 'Enter a date in the future'

    def test_contact_single_date_missing_input(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.SINGLE_DATE.value
            invalid_date = date.today() + relativedelta(days=7)
            DateHelpers.single_date_mock(contact_dates_form, invalid_date, year='')
            assert not contact_dates_form.validate()
            assert contact_dates_form.errors['year'][0] == 'Enter a year'

    def test_contact_single_date_invalid_input(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.SINGLE_DATE.value
            invalid_date = date.today() + relativedelta(days=7)
            DateHelpers.single_date_mock(contact_dates_form, invalid_date, month=14)
            assert not contact_dates_form.validate()
            assert contact_dates_form.errors['month'][0] == 'Enter a month as a number between 1 and 12'

    def test_contact_single_date_range(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.DATE_RANGE.value

            date_range_form = DateRangeForm()
            valid_from_date = date.today() + relativedelta(days=7)
            valid_to_date = valid_from_date + relativedelta(days=7)
            DateHelpers.date_range_mock(date_range_form, valid_from_date, valid_to_date)
            contact_dates_form.date_ranges.append_entry(date_range_form)
            assert contact_dates_form.validate()
            assert validate_date_range_form(date_range_form) == {}
            DateHelpers.remove_date_ranges(contact_dates_form)

    def test_contact_single_date_range_invalid_inputs(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.DATE_RANGE.value

            date_range_form = DateRangeForm()
            invalid_from_date = date.today() + relativedelta(days=7)
            invalid_to_date = invalid_from_date + relativedelta(days=7)
            DateHelpers.date_range_mock(date_range_form, invalid_from_date, invalid_to_date, from_day='', to_year='100')
            contact_dates_form.date_ranges.append_entry(date_range_form)

            # wtf validation is not used on date ranges. It is conducted in the controller so
            # validate() will return True
            assert contact_dates_form.validate()
            form_errors = validate_date_range_form(date_range_form)

            assert form_errors == {
                'from_date_day': 'Enter a day',
                'to_date_year': 'Enter a year as a 4-digit number, like 2000'
            }
            DateHelpers.remove_date_ranges(contact_dates_form)

    def test_contact_single_date_range_invalid_date_in_past(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.DATE_RANGE.value

            date_range_form = DateRangeForm()
            valid_from_date = date.today() + relativedelta(days=7)
            invalid_from_date = date.today() - relativedelta(days=7)
            valid_to_date = valid_from_date + relativedelta(days=14)
            DateHelpers.date_range_mock(date_range_form, invalid_from_date, valid_to_date)
            contact_dates_form.date_ranges.append_entry(date_range_form)

            # wtf validation is not used on date ranges. It is conducted in the controller so
            # validate() will return True
            assert contact_dates_form.validate()
            form_errors = validate_date_range_form(date_range_form)
            assert form_errors == {}
            form_errors = validate_date_ranges(invalid_from_date, valid_to_date)
            assert form_errors == {
                'from_date_year': '\'From\' date is in the past'
            }
            DateHelpers.remove_date_ranges(contact_dates_form)

    def test_contact_single_date_range_invalid_to_date_before_from_date(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.DATE_RANGE.value

            date_range_form = DateRangeForm()
            valid_from_date = date.today() + relativedelta(days=14)
            invalid_to_date = valid_from_date - relativedelta(days=7)
            DateHelpers.date_range_mock(date_range_form, valid_from_date, invalid_to_date)
            contact_dates_form.date_ranges.append_entry(date_range_form)

            # wtf validation is not used on date ranges. It is conducted in the controller so
            # validate() will return True
            assert contact_dates_form.validate()
            form_errors = validate_date_range_form(date_range_form)
            assert form_errors == {}
            form_errors = validate_date_ranges(valid_from_date, invalid_to_date)
            assert form_errors == {
                'to_date_year': "'From' date is after the 'To' date"
            }
            DateHelpers.remove_date_ranges(contact_dates_form)

    def test_contact_multi_date_range_valid(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.DATE_RANGE.value

            date_range_form_1 = DateRangeForm()
            date_range_form_2 = DateRangeForm()

            valid_from_date_1 = date.today() + relativedelta(days=7)
            valid_to_date_1 = valid_from_date_1 + relativedelta(days=7)
            DateHelpers.date_range_mock(date_range_form_1, valid_from_date_1, valid_to_date_1)

            valid_from_date_2 = date.today() + relativedelta(months=3)
            valid_to_date_2 = valid_from_date_2 + relativedelta(months=1)
            DateHelpers.date_range_mock(date_range_form_2, valid_from_date_2, valid_to_date_2)

            contact_dates_form.date_ranges.append_entry(date_range_form_1)
            contact_dates_form.date_ranges.append_entry(date_range_form_2)

            date_range_forms = [date_range_form_1, date_range_form_2]
            date_ranges = {
                0: {'from_date': valid_from_date_1, 'to_date': valid_to_date_1},
                1: {'from_date': valid_from_date_2, 'to_date': valid_to_date_2}
            }

            assert contact_dates_form.validate()
            form_errors = {
                i: validate_date_range_form(date_range_form) for i, date_range_form in enumerate(date_range_forms)
            }
            assert form_errors == {0: {}, 1: {}}

            form_errors = {
                i: validate_date_ranges(
                    date_range['from_date'], date_range['to_date']) for i, date_range in date_ranges.items()
            }
            assert form_errors == {0: {}, 1: {}}
            DateHelpers.remove_date_ranges(contact_dates_form)

    def test_contact_multi_date_range_invalid(self, app):
        with app.test_request_context():
            contact_dates_form = ContactDatesForm()
            contact_dates_form.contactDatesCheck.data = ContactDatesAvoid.DATE_RANGE.value

            date_range_form_1 = DateRangeForm()
            date_range_form_2 = DateRangeForm()
            invalid_from_date_1 = date.today() + relativedelta(days=7)
            invalid_to_date_1 = invalid_from_date_1 + relativedelta(days=7)
            erroneous_fields = {
                'from_month': '14',
                'to_day': ''
            }
            DateHelpers.date_range_mock(date_range_form_1, invalid_from_date_1, invalid_to_date_1, **erroneous_fields)

            valid_from_date_2 = date.today() + relativedelta(months=3)
            invalid_to_date_2 = valid_from_date_2 - relativedelta(months=1)
            DateHelpers.date_range_mock(date_range_form_2, valid_from_date_2, invalid_to_date_2)

            contact_dates_form.date_ranges.append_entry(date_range_form_1)
            contact_dates_form.date_ranges.append_entry(date_range_form_2)

            date_range_forms = [date_range_form_1, date_range_form_2]
            date_ranges = {
                0: {'from_date': invalid_from_date_1, 'to_date': invalid_to_date_1},
                1: {'from_date': valid_from_date_2, 'to_date': invalid_to_date_2}
            }

            assert contact_dates_form.validate()
            form_errors = {
                i: validate_date_range_form(date_range_form) for i, date_range_form in enumerate(date_range_forms)
            }
            assert form_errors == {
                0: {'from_date_month': 'Enter a month as a number between 1 and 12', 'to_date_day': 'Enter a day'},
                1: {}
            }
            form_errors = {
                i: validate_date_ranges(
                    date_range['from_date'], date_range['to_date']) for i, date_range in date_ranges.items()
            }
            assert form_errors == {0: {}, 1: {'to_date_year': "'From' date is after the 'To' date"}}
            DateHelpers.remove_date_ranges(contact_dates_form)
