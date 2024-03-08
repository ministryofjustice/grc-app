import email_validator
from flask_babel import LazyString
from wtforms.validators import DataRequired, ValidationError, StopValidation, Email


class LazyStopValidation(StopValidation):

    def __init__(self, lazy_message: LazyString = None, *args):
        Exception.__init__(self, lazy_message, *args)


class LazyValidationError(ValidationError):

    def __init__(self, lazy_message: LazyString = None, *args):
        ValueError.__init__(self, lazy_message, *args)


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
