import email_validator
from .lazy_errors import LazyValidationError, LazyStopValidation
from collections.abc import Iterable
from flask_babel import LazyString
from grc.utils.form_custom_validators import MultiFileAllowed, Integer
from werkzeug.datastructures import FileStorage
from wtforms.validators import DataRequired, ValidationError, StopValidation, Email


class LazyDataRequired(DataRequired):

    def __init__(self, message=None, lazy_message: LazyString = None):
        super().__init__(message)
        self.message = message
        self.lazy_message = lazy_message
        self.field_flags = {"required": True}

    def __call__(self, form, field):
        if field.data and (not isinstance(field.data, str) or field.data.strip()):
            return

        field.errors[:] = []

        if self.lazy_message:
            raise LazyStopValidation(self.lazy_message)

        if self.message is None:
            message = field.gettext("This field is required.")
        else:
            message = self.message

        raise StopValidation(message)


class LazyEmail(Email):

    def __init__(self, message=None, lazy_message: LazyString = None):
        super().__init__(message)
        self.message = message
        self.lazy_message = lazy_message

    def __call__(self, form, field):
        try:
            if field.data is None:
                raise email_validator.EmailNotValidError()
            email_validator.validate_email(
                field.data,
                check_deliverability=self.check_deliverability,
                allow_smtputf8=self.allow_smtputf8,
                allow_empty_local=self.allow_empty_local,
            )
        except email_validator.EmailNotValidError as e:

            if self.lazy_message:
                raise LazyValidationError(self.lazy_message)

            message = self.message
            if message is None:
                if self.granular_message:
                    message = field.gettext(e)
                else:
                    message = field.gettext("Invalid email address.")
            raise ValidationError(message) from e


class LazyMultiFileAllowed(MultiFileAllowed):
    def __init__(self, upload_set, message=None, lazy_message: LazyString = None):
        super().__init__(upload_set, message)
        self.upload_set = upload_set
        self.message = message
        self.lazy_message = lazy_message

    def __call__(self, form, field):
        if not (all(isinstance(item, FileStorage) for item in field.data) and field.data):
            return

        for data in field.data:
            filename = data.filename.lower()

            if isinstance(self.upload_set, Iterable):
                if any(filename.endswith('.' + x) for x in self.upload_set):
                    return

                if self.lazy_message:
                    raise LazyStopValidation(self.lazy_message)

                raise StopValidation(self.message or field.gettext(
                    'File does not have an approved extension: {extensions}'
                ).format(extensions=', '.join(self.upload_set)))

            if not self.upload_set.file_allowed(field.data, filename):

                if self.lazy_message:
                    raise LazyStopValidation(self.lazy_message)

                raise StopValidation(self.message or field.gettext(
                    'File does not have an approved extension.'
                ))


class LazyInteger(Integer):
    def __init__(self, min_=None, max_=None, lazy_message=None, message=None, validators=None):
        super().__init__(message, validators)
        self.min = min_
        self.max = max_
        self.message = message
        self.validators = validators
        self.lazy_message = lazy_message

    def __call__(self, form, field):

        string_value: str = field.data
        message = self.lazy_message or self.message
        try:
            int_value = int(string_value)

            if self.min and int_value < self.min:
                raise ValidationError(
                    message if message else f"{field} must be at least {self.min}"
                )

            if self.max and int_value > self.max:
                raise ValidationError(
                    message if message else f"{field} must be at most {self.max}"
                )

        except Exception as e:
            raise ValidationError(
                message if message else f"{field} must be a whole number"
            )

        if self.validators:
            for validator in self.validators:
                validator(form, field)
