import os
import re
import pathlib
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from flask import session, current_app
from wtforms.validators import DataRequired, ValidationError, StopValidation
from werkzeug.datastructures import FileStorage
from datetime import date
from grc.business_logic.constants.base import BaseConstants as c
from grc.business_logic.data_store import DataStore
from grc.lazy.lazy_errors import LazyValidationError
from grc.models import db, Application
from grc.utils.security_code import is_security_code_valid
from grc.utils.reference_number import reference_number_is_valid
from grc.utils.logger import LogLevel, Logger

logger = Logger()


class StrictRequiredIf(DataRequired):
    """Validator which makes a field required if another field is set and has a specific value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

    """
    field_flags = {'requiredif': True}

    def __init__(self, other_field_name, other_field_value, message=None, validators=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.other_field_value = other_field_value
        self.message = message
        self.validators = validators

    def __call__(self, form, field):

        other_field = form[self.other_field_name]

        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        if (str(other_field.data) == str(self.other_field_value) or
           (isinstance(self.other_field_value, list) and other_field.data in self.other_field_value) or
           (isinstance(other_field.data, list) and self.other_field_value in other_field.data)):
            super(StrictRequiredIf, self).__call__(form, field)
            if self.validators:
                for validator in self.validators:
                    validator(form, field)


class Integer(DataRequired):
    def __init__(self, min: int = None, max: int = None, message: str = None, validators=None):
        self.min = min
        self.max = max
        self.message = message
        self.validators = validators

    def __call__(self, form, field):

        string_value: str = field.data

        try:
            int_value = int(string_value)

            if self.min and int_value < self.min:
                raise ValidationError(
                    self.message if self.message else f"{field} must be at least {self.min}"
                )

            if self.max and int_value > self.max:
                raise ValidationError(
                    self.message if self.message else f"{field} must be at most {self.max}"
                )

        except Exception as e:
            raise ValidationError(
                self.message if self.message else f"{field} must be a whole number"
            )

        if self.validators:
            for validator in self.validators:
                validator(form, field)


def validate_security_code_admin(form, field):
    is_test = True if os.getenv('TEST_URL', '') != '' or os.getenv('FLASK_ENV', '') == 'development' else False

    if is_test and field.data == '11111':
        return

    if not is_security_code_valid(session.get('email'), field.data, True):
        raise ValidationError('Enter the security code that we emailed you')


def validate_security_code(form, field):
    is_test = True if os.getenv('TEST_URL', '') != '' or os.getenv('FLASK_ENV', '') == 'development' else False

    if is_test and field.data == '11111':
        return

    if not is_security_code_valid(session.get('email'), field.data, False):
        raise LazyValidationError(c.INVALID_SECURITY_CODE)


def validate_reference_number(form, field):
    validated_email = session.get('email')
    if not reference_number_is_valid(field.data, validated_email):
        email = logger.mask_email_address(validated_email) if validated_email in session else 'Unknown user'
        reference_number = f"{field.data[0: 2]}{'*' * (len(field.data) - 4)}{field.data[-2:]}"
        logger.log(LogLevel.WARN, f"{email} entered an incorrect reference number ({reference_number})")
        raise LazyValidationError(c.INVALID_REFERENCE_NUMBER_ERROR)


def validate_gov_uk_email_address(form, field):
    email_address: str = field.data
    if not email_address.endswith('.gov.uk'):
        raise ValidationError('Enter a .gov.uk email address')


def validate_password_strength(form, field):
    password = field.data
    errors = []
    if len(password) < 8:
        errors.append('Password too short')

    if not re.search(r'\d', password):
        errors.append('Password is missing a number')

    if not re.search(r'[A-Z]', password):
        errors.append('Password is missing an uppercase char')

    if not re.search(r'[a-z]', password):
        errors.append('Password is missing a lowercase char')

    if not re.search(r'\W', password):
        errors.append('Password is missing a special char')

    if errors:
        logger.log(LogLevel.INFO, message=f'Error resetting password with following errors = {errors}')
        raise ValidationError('Your password needs to contain 8 or more characters, a lower case letter, an upper case'
                              ' letter, a number and a special character')


def validate_address_field(form, field):
    if not field.data:
        return

    match = re.search('^[a-zA-Z0-9- ]*$', field.data)
    if match is None:
        messages = defaultdict(lambda: c.ADDRESS_ERROR)
        error_messages = {
            'address_line_one': c.ADDRESS_LINE_ONE_ERROR,
            'address_line_two': c.ADDRESS_LINE_TWO_ERROR,
            'town': c.ADDRESS_TOWN_OR_CITY_ERROR,
        }
        messages.update(error_messages)
        raise LazyValidationError(messages[field.label.field_id])


def validate_postcode(form, field):
    if not field.data:
        return

    match = re.search('^([A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]? ?[0-9][A-Za-z]{2}|[Gg][Ii][Rr] ?0[Aa]{2})$',
                      field.data)
    if match is None:
        raise LazyValidationError(c.ENTER_VALID_POSTCODE_ERROR)


def validate_date_of_birth(form, field):
    if form['day'].errors or form['month'].errors:
        return

    try:
        d = int(form['day'].data)
        m = int(form['month'].data)
        y = int(form['year'].data)
        date_of_birth = date(day=d, month=m, year=y)
    except ValueError as error:
        raise LazyValidationError(c.ENTER_VALID_DATE_ERROR)

    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

    if age < 18:
        raise LazyValidationError(c.ABOVE_AGE_ERROR)

    if age > 110:
        raise LazyValidationError(c.BELOW_AGE_ERROR)

    reference_number = session.get('reference_number')
    application_data = DataStore.load_application(reference_number)
    transition_date = application_data.personal_details_data.transition_date
    statutory_declaration_date = application_data.personal_details_data.statutory_declaration_date

    if transition_date and date_of_birth > transition_date:
        raise LazyValidationError(c.DATE_OF_BIRTH_BEFORE_TRANSITION_ERROR)

    if statutory_declaration_date and date_of_birth > statutory_declaration_date:
        raise LazyValidationError(c.DATE_OF_BIRTH_BEFORE_TRANSITION_ERROR)


def validate_date_of_transition(form, field):
    if form['transition_date_month'].errors:
        return

    try:
        transition_date_month = int(form['transition_date_month'].data)
        transition_date_year = int(form['transition_date_year'].data)
        date_of_transition = date(transition_date_year, transition_date_month, 1)
    except Exception as e:
        raise LazyValidationError(c.INVALID_YEAR_ERROR)

    earliest_date_of_transition_years = 100
    earliest_date_of_transition = date.today() - relativedelta(years=earliest_date_of_transition_years)

    if date_of_transition < earliest_date_of_transition:
        raise LazyValidationError(c.DATE_BEFORE_EARLIEST_ERROR)

    if date_of_transition > date.today():
        raise LazyValidationError(c.ENTER_DATE_IN_PAST_ERROR)

    reference_number = session['reference_number']
    application_record = db.session.query(Application).filter_by(reference_number=reference_number).first()
    application_created_date = date(application_record.created.year, application_record.created.month,
                                    application_record.created.day)
    application_data = application_record.application_data()

    if application_data.confirmation_data.gender_recognition_outside_uk:
        return

    latest_transition_years = 2
    latest_transition_date = application_created_date - relativedelta(years=latest_transition_years)
    if date_of_transition > latest_transition_date:
        raise LazyValidationError(c.ENTER_DATE_2_YEARS_BEFORE_APP_CREATED_ERROR)


def validate_statutory_declaration_date(form, field):
    if form['statutory_declaration_date_day'].errors or form['statutory_declaration_date_month'].errors:
        return

    try:
        statutory_declaration_date_day = int(form['statutory_declaration_date_day'].data)
        statutory_declaration_date_month = int(form['statutory_declaration_date_month'].data)
        statutory_declaration_date_year = int(form['statutory_declaration_date_year'].data)
        statutory_declaration_date = date(statutory_declaration_date_year, statutory_declaration_date_month,
                                          statutory_declaration_date_day)
    except Exception as e:
        raise LazyValidationError(c.INVALID_YEAR_ERROR)

    earliest_statutory_declaration_date_years = 100
    earliest_statutory_declaration_date = date.today() - relativedelta(
        years=earliest_statutory_declaration_date_years)

    if statutory_declaration_date < earliest_statutory_declaration_date:
        raise LazyValidationError(c.DATE_BEFORE_EARLIEST_ERROR)

    latest_statutory_declaration_date = date.today()
    if statutory_declaration_date > latest_statutory_declaration_date:
        raise LazyValidationError(c.ENTER_DATE_IN_PAST_ERROR)

    reference_number = session['reference_number']
    application_data = DataStore.load_application(reference_number)
    transition_date = application_data.personal_details_data.transition_date
    if statutory_declaration_date < transition_date:
        raise LazyValidationError(c.STAT_DEC_DATE_BEFORE_TRANSITION_DATE_ERROR)

def validate_date_range(form, field):
    if form['start_date_day'].errors or form['start_date_month'].errors:
        return

    if form['end_date_day'].errors or form['end_date_month'].errors:
        return

    errors = []

    if field.id == 'start_date_year':
        errors_start, start_date = validate_date(form, 'start')
        errors.extend(errors_start)

    if field.id == 'end_date_year':
        errors_start, start_date = validate_date(form, 'start')
        errors_end, end_date = validate_date(form, 'end')
        errors.extend(errors_end)

        if start_date is not None and end_date is not None and end_date < start_date:
            errors.append('The end date cannot be earlier than the start date')

    if errors:
        for error in errors:
            logger.log(LogLevel.ERROR, message=error)
            raise ValidationError(error)

def validate_date(form, date_type):
    errors = []
    try:
        day = int(form[f'{date_type}_date_day'].data)
        month = int(form[f'{date_type}_date_month'].data)
        year = int(form[f'{date_type}_date_year'].data)

        validated_date = date(year, month, day)
        return errors, validated_date

    except ValueError as e:
        errors.append(f'Enter a valid {date_type} date: {e}')
        return errors, None

def validate_national_insurance_number(form, field):
    if not field.data:
        return

    data = field.data.replace(' ', '').upper()
    match = re.search(
        r'^(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)([A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}[A-D]$',
        data
    )
    if match is None:
        raise LazyValidationError(c.ENTER_VALID_NI_NUMBER_ERROR)


def validate_phone_number(form, field):
    if not field.data:
        return

    phone = re.sub(r'[\s\-]', '', field.data)

    match = re.fullmatch(r'(\+|00)?\d{7,15}', phone)
    if match is None:
        raise LazyValidationError(c.ENTER_VALID_PHONE_NUMBER_ERROR)


def validate_hwf_reference_number(form, field):
    """
    Regex to validate HWF reference number separated into 2 parts by an OR '|':
    1. 11 chars long in the format of HWF-123-ABC
    2. 9 chars long in format of HWF123ABC
    """
    if not field.data:
        return

    match = re.search(
        '^(((?=.{11}$)(?=HWF-)+([a-zA-Z0-9])+((-[a-zA-Z0-9]{3})+))|((?=.{9}$)(?=^HWF)(?=[a-zA-Z0-9]).*))+$',
        field.data
    )
    if match is None:
        raise LazyValidationError(c.INVALID_HWF_REFERENCE_NUMBER)


def validate_single_date(form, field):
    if form['day'].errors or form['month'].errors:
        return

    try:
        day = int(form['day'].data)
        month = int(form['month'].data)
        year = int(form['year'].data)
        date_entered = date(year, month, day)
    except ValueError as e:
        logger.log(LogLevel.ERROR, message=f'Error validating single date: {e}')
        raise LazyValidationError(c.ENTER_VALID_DATE_ERROR)

    if date_entered < date.today():
        raise LazyValidationError(c.ENTER_DATE_IN_FUTURE_ERROR)


def validate_date_range_form(date_ranges_form):
    form_errors = dict()
    from_date_day_entered = True
    from_date_month_entered = True
    from_date_year_entered = True
    to_date_day_entered = True
    to_date_month_entered = True
    to_date_year_entered = True

    if not date_ranges_form.from_date_day.data:
        form_errors['from_date_day'] = c.ENTER_DAY_ERROR
        from_date_day_entered = False

    if not date_ranges_form.from_date_month.data:
        form_errors['from_date_month'] = c.ENTER_MONTH_ERROR
        from_date_month_entered = False

    if not date_ranges_form.from_date_year.data:
        form_errors['from_date_year'] = c.ENTER_YEAR_ERROR
        from_date_year_entered = False

    if not date_ranges_form.to_date_day.data:
        form_errors['to_date_day'] = c.ENTER_DAY_ERROR
        to_date_day_entered = False

    if not date_ranges_form.to_date_month.data:
        form_errors['to_date_month'] = c.ENTER_MONTH_ERROR
        to_date_month_entered = False

    if not date_ranges_form.to_date_year.data:
        form_errors['to_date_year'] = c.ENTER_YEAR_ERROR
        to_date_year_entered = False

    if from_date_day_entered and (int(date_ranges_form.from_date_day.data) < 1 or
                                  int(date_ranges_form.from_date_day.data) > 31):
        form_errors['from_date_day'] = c.ENTER_VALID_DAY_ERROR

    if to_date_day_entered and (int(date_ranges_form.to_date_day.data) < 1 or
                                int(date_ranges_form.to_date_day.data) > 31):
        form_errors['to_date_day'] = c.ENTER_VALID_DAY_ERROR

    if from_date_month_entered and (int(date_ranges_form.from_date_month.data) < 1 or
                                    int(date_ranges_form.from_date_month.data) > 12):
        form_errors['from_date_month'] = c.ENTER_VALID_MONTH_ERROR

    if to_date_month_entered and (int(date_ranges_form.to_date_month.data) < 1 or
                                  int(date_ranges_form.to_date_month.data) > 12):
        form_errors['to_date_month'] = c.ENTER_VALID_MONTH_ERROR

    if from_date_year_entered and int(date_ranges_form.from_date_year.data) < 1000:
        form_errors['from_date_year'] = c.ENTER_VALID_YEAR_ERROR

    if to_date_year_entered and int(date_ranges_form.to_date_year.data) < 1000:
        form_errors['to_date_year'] = c.ENTER_VALID_YEAR_ERROR

    return form_errors


def validate_date_ranges(from_date, to_date):
    form_errors = dict()

    if from_date < date.today():
        form_errors['from_date_year'] = c.CONTACT_FROM_DATE_IN_PAST_ERROR

    if to_date < date.today():
        form_errors['to_date_year'] = c.CONTACT_TO_DATE_IN_PAST_ERROR

    if from_date > to_date:
        form_errors['to_date_year'] = c.CONTACT_FROM_DATE_AFTER_TO_DATE_ERROR

    return form_errors


class SingleFileAllowed:
    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        if not field.data and not isinstance(field.data, FileStorage):
            return

        filename = field.data.filename.lower()

        if pathlib.Path(filename).suffix[1:] in self.upload_set:
            return

        raise StopValidation(self.message or field.gettext(
            'File does not have an approved extension: {extensions}'
        ).format(extensions=', '.join(self.upload_set)))


class MultiFileAllowed:
    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        if not (field.data and all(isinstance(item, FileStorage) for item in field.data)):
            return

        for data in field.data:
            filename = data.filename.lower()
            if pathlib.Path(filename).suffix[1:] in self.upload_set:
                continue

            raise StopValidation(self.message or field.gettext(
                'File does not have an approved extension: {extensions}'
            ).format(extensions=', '.join(self.upload_set)))



def validate_file_size_limit(form, field):
    if not field.data:
        return

    file_size_limit = form.file_size_limit_mb if form.file_size_limit_mb else 10
    max_bytes = file_size_limit * 1024 * 1024

    file_size = field.data.read()
    field.data.seek(0)
    if len(file_size) == 0:
        raise ValidationError('The selected file is empty. Check that the file you are uploading has the'
                              ' content you expect')
    elif len(file_size) > max_bytes:
        raise ValidationError(f'The selected file must be smaller than {file_size_limit}MB')


def validate_multiple_files_size_limit(form, field):
    if not field.data:
        return

    file_size_limit = form.file_size_limit_mb if form.file_size_limit_mb else 10
    max_bytes = file_size_limit * 1024 * 1024
    for data in field.data:
        file_size = data.read()
        data.seek(0)
        if len(file_size) == 0:
            raise LazyValidationError(c.FILE_EMPTY_ERROR)
        elif len(file_size) > max_bytes:
            raise LazyValidationError(c.FILE_SIZE_LIMIT_ERROR)


def file_virus_scan(form, field):
    if 'AV_API' not in current_app.config.keys() or not current_app.config['AV_API']:
        return

    if not field.data:
        return

    logger.log(LogLevel.INFO, message=f'Scanning {current_app.config["AV_API"]}')

    from pyclamd import ClamdNetworkSocket
    url = current_app.config['AV_API']
    url = url.replace('http://', '')
    url = url.replace('https://', '')
    cd = ClamdNetworkSocket(host=url, port=3310, timeout=None)
    uploaded_files = field.data

    for uploaded_file in uploaded_files:
        uploaded_file.stream.seek(0)

        if not cd.ping():
            raise LazyValidationError(c.VIRUS_SCANNER_ERROR)

        results = cd.scan_stream(uploaded_file.stream.read())
        if results:
            res_type, res_msg = results['stream']
            if res_type == 'FOUND':
                raise LazyValidationError(c.FILE_HAS_VIRUS_ERROR)
            logger.log(LogLevel.ERROR, message='Error scanning uploaded file')
            raise ValidationError('Error scanning uploaded file')
        uploaded_file.stream.seek(0)

def validate_email_matches_application(form, field):
    reference_number = session.get('reference_number')

    application = Application.query.filter_by(reference_number=reference_number).first()
    if not application:
        raise ValidationError("No application found for the given reference number.")

    if field.data != application.email:
        raise ValidationError("This email address does not match our records for the reference number you provided.")

