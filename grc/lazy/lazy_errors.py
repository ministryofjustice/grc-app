from flask_babel.speaklater import LazyString
from wtforms.validators import ValidationError, StopValidation


class LazyStopValidation(StopValidation):

    def __init__(self, lazy_message: LazyString = None, *args):
        Exception.__init__(self, lazy_message, *args)


class LazyValidationError(ValidationError):

    def __init__(self, lazy_message: LazyString = None, *args):
        ValueError.__init__(self, lazy_message, *args)
