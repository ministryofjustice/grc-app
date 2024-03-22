from grc.models import Application
from grc.utils.logger import Logger, LogLevel

logger = Logger()


def reference_number_string(reference_number):
    trimmed_reference = reference_number.replace('-', '').replace(' ', '').upper()
    formatted_reference = trimmed_reference[0: 4] + '-' + trimmed_reference[4: 8]
    return formatted_reference


def reference_number_is_valid(reference, email, is_admin):
    reference = reference.replace('-', '').replace(' ', '').upper()

    if is_admin and email is None:
        application = Application.query.filter_by(reference_number=reference).first()
        if application:
            return True
        return False

    application = Application.query.filter_by(reference_number=reference, email=email).first()

    if application is None:
        logger.log(LogLevel.INFO, message=f"An application with reference number {reference} does not exist")
        return False
    return True
