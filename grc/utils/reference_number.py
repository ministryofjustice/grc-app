from grc.models import Application, ApplicationStatus
from grc.utils.logger import Logger, LogLevel

logger = Logger()


def reference_number_string(reference_number):
    trimmed_reference = reference_number.replace('-', '').replace(' ', '').upper()
    formatted_reference = trimmed_reference[0: 4] + '-' + trimmed_reference[4: 8]
    return formatted_reference


def reference_number_is_valid(reference, email):
    reference = reference.replace('-', '').replace(' ', '').upper()
    application = Application.query.filter_by(reference_number=reference, email=email).first()

    if application is None:
        logger.log(LogLevel.INFO, message=f"An application with reference number {reference} does not exist")
        return False
    return True


def reference_number_is_valid_admin(reference):
    reference = reference.replace('-', '').replace(' ', '').upper()
    application = Application.query.filter_by(reference_number=reference).filter(
        Application.status.in_([ApplicationStatus.SUBMITTED, ApplicationStatus.DOWNLOADED, ApplicationStatus.COMPLETED])
    ).first()

    if application is None:
        logger.log(LogLevel.INFO, message=f"An application with reference number {reference} does not exist or has"
                                          f" not been submitted yet")
        return False
    return True
