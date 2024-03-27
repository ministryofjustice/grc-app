import os
import re
from dateutil.relativedelta import relativedelta
from flask import request, session, current_app
from wtforms.validators import DataRequired, ValidationError, StopValidation
from werkzeug.datastructures import FileStorage
from collections.abc import Iterable
from datetime import date
from grc.business_logic.data_store import DataStore
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


def validate_security_code(form, field):
    is_test = True if os.getenv('TEST_URL', '') != '' or os.getenv('FLASK_ENV', '') == 'development' else False

    if is_test and field.data == '11111':
        return

    is_admin = True if 'userType' in session else False
    if not is_security_code_valid(session.get('email'), field.data, is_admin):
        raise ValidationError('Enter the security code that we emailed you')


def validate_reference_number(form, field):
    validated_email = session.get('validatedEmail')
    if not reference_number_is_valid(field.data, validated_email):
        email = logger.mask_email_address(validated_email) if validated_email in session else 'Unknown user'
        reference_number = f"{field.data[0: 2]}{'*' * (len(field.data) - 4)}{field.data[-2:]}"
        logger.log(LogLevel.WARN, f"{email} entered an incorrect reference number ({reference_number})")
        raise ValidationError('Enter a valid reference number')


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
        raise ValidationError(f'Enter a valid {field.label.text.lower()}')


def validate_postcode(form, field):
    if not field.data:
        return

    match = re.search('^([A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]? ?[0-9][A-Za-z]{2}|[Gg][Ii][Rr] ?0[Aa]{2})$',
                      field.data)
    if match is None:
        raise ValidationError('Enter a valid postcode')


def validate_date_of_birth(form, field):
    if form['day'].errors or form['month'].errors:
        return

    try:
        d = int(form['day'].data)
        m = int(form['month'].data)
        y = int(form['year'].data)
        date_of_birth = date(day=d, month=m, year=y)
    except ValueError as error:
        raise ValidationError('Enter a valid date')

    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

    if age < 18:
        raise ValidationError('You need to be at least 18 years old to apply')

    if age > 110:
        raise ValidationError('You need to be less than 110 years old to apply')

    reference_number = session.get('reference_number')
    application_data = DataStore.load_application(reference_number)
    transition_date = application_data.personal_details_data.transition_date
    statutory_declaration_date = application_data.personal_details_data.statutory_declaration_date

    if transition_date and date_of_birth > transition_date:
        raise ValidationError('Your date of birth must be before your transition date and statutory declaration'
                              + ' date')

    if statutory_declaration_date and date_of_birth > statutory_declaration_date:
        raise ValidationError('Your date of birth must be before your transition date and statutory declaration'
                              + ' date')


def validateDateOfTransiton(form, field):
    if not form['transition_date_month'].errors:
        try:
            transition_date_month = int(form['transition_date_month'].data)
            transition_date_year = int(form['transition_date_year'].data)
            date_of_transition = date(transition_date_year, transition_date_month, 1)
        except Exception as e:
            raise ValidationError('Enter a valid year')
    
        earliest_date_of_transition_years = 100
        earliest_date_of_transition = date.today() - relativedelta(years=earliest_date_of_transition_years)

        reference_number = session['reference_number']
        application_record = db.session.query(Application).filter_by(
            reference_number=reference_number
        ).first()
        application_data = DataStore.load_application(reference_number)

        latest_transition_years = 2
        application_created_date = date(
            application_record.created.year,
            application_record.created.month,
            application_record.created.day
        )
        latest_transition_date = application_created_date - relativedelta(years=latest_transition_years)

        if date_of_transition < earliest_date_of_transition:
            raise ValidationError(f'Enter a date within the last {earliest_date_of_transition_years} years')

        if date_of_transition > date.today():
            raise ValidationError('Enter a date in the past')

        if date_of_transition > latest_transition_date \
                and not application_data.confirmation_data.gender_recognition_outside_uk:
            raise ValidationError(f'Enter a date at least {latest_transition_years} years before your application')


def validateStatutoryDeclarationDate(form, field):
    if not form['statutory_declaration_date_day'].errors and not form['statutory_declaration_date_month'].errors:
        try:
            statutory_declaration_date_day = int(form['statutory_declaration_date_day'].data)
            statutory_declaration_date_month = int(form['statutory_declaration_date_month'].data)
            statutory_declaration_date_year = int(form['statutory_declaration_date_year'].data)
            statutory_declaration_date = date(statutory_declaration_date_year, statutory_declaration_date_month, statutory_declaration_date_day)
        except Exception as e:
            raise ValidationError('Enter a valid year')

        application_record = db.session.query(Application).filter_by(
            reference_number=session['reference_number']
        ).first()
        transition_date = application_record.application_data().personal_details_data.transition_date
        earliest_statutory_declaration_date_years = 100
        earliest_statutory_declaration_date = date.today() - relativedelta(years=earliest_statutory_declaration_date_years)

        if statutory_declaration_date < earliest_statutory_declaration_date:
            raise ValidationError(f'Enter a date within the last {earliest_statutory_declaration_date_years} years')

        latest_statutory_declaration_date = date.today()

        if statutory_declaration_date > latest_statutory_declaration_date:
            raise ValidationError('Enter a date in the past')

        if statutory_declaration_date < transition_date:
            raise ValidationError('Enter a date that does not precede your transition date')


def validateDateRange(form, field):
    if not form['start_date_day'].errors and not form['start_date_month'].errors and not form['end_date_day'].errors and not form['end_date_month'].errors:
        try:
            start_date_day = int(form['start_date_day'].data)
            start_date_month = int(form['start_date_month'].data)
            start_date_year = int(form['start_date_year'].data)

            start_date = date(start_date_year, start_date_month, start_date_day)
        except Exception as e:
            raise ValidationError('Enter a valid start year')

        try:
            end_date_day = int(form['end_date_day'].data)
            end_date_month = int(form['end_date_month'].data)
            end_date_year = int(form['end_date_year'].data)

            end_date = date(end_date_year, end_date_month, end_date_day)
        except Exception as e:
            raise ValidationError('Enter a valid end year')


def validateNationalInsuranceNumber(form, field):

    # https://www.gov.uk/hmrc-internal-manuals/national-insurance-manual/nim39110
    # https://stackoverflow.com/questions/17928496/use-regex-to-validate-a-uk-national-insurance-no-nino-in-an-html5-pattern-attri
    if not (field.data is None or field.data == ''):
        data = field.data.replace(' ', '').upper()
        match = re.search('^(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}[A-D]{1}$', data)
        if match is None:
            raise ValidationError('Enter a valid National Insurance number')


def validatePhoneNumber(form, field):
    if not(field.data is None or field.data == ''):
        match = re.search('^[0-9]+$', field.data)
        if match is None:
            raise ValidationError('Enter a valid phone number')


def validateHWFReferenceNumber(form, field):
    if not (field.data is None or field.data == ''):
        """
        Regex to validate HWF reference number separated into 2 parts by an OR '|':
        1. 11 chars long in the format of HWF-123-ABC
        2. 9 chars long in format of HWF123ABC
        """
        match = re.search(
            '^(((?=.{11}$)(?=HWF-)+([a-zA-Z0-9])+((-[a-zA-Z0-9]{3})+))|((?=.{9}$)(?=^HWF)(?=[a-zA-Z0-9]).*))+$',
            field.data
        )
        if match is None:
            raise ValidationError(f'Enter a valid \'Help with fees\' reference number')


def validate_single_date(form, field):
    if not form['day'].errors and not form['month'].errors:
        try:
            day = int(form['day'].data)
            month = int(form['month'].data)
            year = int(form['year'].data)
            date_entered = date(year, month, day)
        except Exception as e:
            print(f"ERROR => {e}", flush=True)
            raise ValidationError('Enter a valid date')

        if date_entered < date.today():
            raise ValidationError('Enter a date in the future')


def validate_date_range_form(date_ranges_form):
    form_errors = dict()
    from_date_day_entered = True
    from_date_month_entered = True
    from_date_year_entered = True
    to_date_day_entered = True
    to_date_month_entered = True
    to_date_year_entered = True

    if not date_ranges_form.from_date_day.data:
        form_errors['from_date_day'] = 'Enter a day'
        from_date_day_entered = False

    if not date_ranges_form.from_date_month.data:
        form_errors['from_date_month'] = 'Enter a month'
        from_date_month_entered = False

    if not date_ranges_form.from_date_year.data:
        form_errors['from_date_year'] = 'Enter a year'
        from_date_year_entered = False

    if not date_ranges_form.to_date_day.data:
        form_errors['to_date_day'] = 'Enter a day'
        to_date_day_entered = False

    if not date_ranges_form.to_date_month.data:
        form_errors['to_date_month'] = 'Enter a month'
        to_date_month_entered = False

    if not date_ranges_form.to_date_year.data:
        form_errors['to_date_year'] = 'Enter a year'
        to_date_year_entered = False

    if from_date_day_entered and (int(date_ranges_form.from_date_day.data) < 1 or
                                  int(date_ranges_form.from_date_day.data) > 31):
        form_errors['from_date_day'] = 'Enter a day as a number between 1 and 31'

    if to_date_day_entered and (int(date_ranges_form.to_date_day.data) < 1 or
                                int(date_ranges_form.to_date_day.data) > 31):
        form_errors['to_date_day'] = 'Enter a day as a number between 1 and 31'

    if from_date_month_entered and (int(date_ranges_form.from_date_month.data) < 1 or
                                    int(date_ranges_form.from_date_month.data) > 12):
        form_errors['from_date_month'] = 'Enter a month as a number between 1 and 12'

    if to_date_month_entered and (int(date_ranges_form.to_date_month.data) < 1 or
                                  int(date_ranges_form.to_date_month.data) > 12):
        form_errors['to_date_month'] = 'Enter a month as a number between 1 and 12'

    if from_date_year_entered and int(date_ranges_form.from_date_year.data) < 1000:
        form_errors['from_date_year'] = 'Enter a year as a 4-digit number, like 2000'

    if to_date_year_entered and int(date_ranges_form.to_date_year.data) < 1000:
        form_errors['to_date_year'] = 'Enter a year as a 4-digit number, like 2000'

    return form_errors


def validate_date_ranges(from_date, to_date):
    form_errors = dict()

    if from_date < date.today():
        form_errors['from_date_year'] = '\'From\' date is in the past'

    if to_date < date.today():
        form_errors['to_date_year'] = '\'To\' date is in the past'

    if from_date > to_date:
        form_errors['to_date_year'] = '\'From\' date is after the \'To\' date'

    return form_errors


class MultiFileAllowed(object):
    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        if not (field.data and all(isinstance(item, FileStorage) for item in field.data)):
            return

        for data in field.data:
            filename = data.filename.lower()

            if isinstance(self.upload_set, Iterable):
                if any(filename.endswith('.' + x) for x in self.upload_set):
                    return

                raise StopValidation(self.message or field.gettext(
                    'File does not have an approved extension: {extensions}'
                ).format(extensions=', '.join(self.upload_set)))

def fileSizeLimit(max_size_in_mb):
    max_bytes = max_size_in_mb*1024*1024

    def file_length_check(form, field):
        for data in field.data:
            file_size = data.read()
            data.seek(0)
            if len(file_size) == 0:
                raise ValidationError('The selected file is empty. Check that the file you are uploading has the content you expect')
            elif len(file_size) > max_bytes:
                raise ValidationError(f'The selected file must be smaller than {max_size_in_mb}MB')

    return file_length_check


def fileVirusScan(form, field):
    if ('AV_API' not in current_app.config.keys()) or (not current_app.config['AV_API']):
        return
    if (field.name not in request.files or request.files[field.name].filename == ''):
        return

    print('Scanning %s' % current_app.config['AV_API'], flush=True)

    from pyclamd import ClamdNetworkSocket
    url = current_app.config['AV_API']
    url = url.replace('http://', '')
    url = url.replace('https://', '')
    cd = ClamdNetworkSocket(host=url, port=3310, timeout=None)
    uploaded_files = request.files.getlist(field.name)

    for uploaded_file in uploaded_files:
        uploaded_file.stream.seek(0)

        if not cd.ping():
            raise ValidationError('Unable to communicate with virus scanner')

        results = cd.scan_stream(uploaded_file.stream.read())
        if results is None:
            uploaded_file.stream.seek(0)
        else:
            res_type, res_msg = results['stream']
            if res_type == 'FOUND':
                raise ValidationError('The selected file contains a virus')
            else:
                print('Error scanning uploaded file', flush=True)
