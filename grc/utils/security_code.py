import random
from datetime import datetime, timedelta
from grc.external_services.gov_uk_notify import GovUkNotify
from grc.models import db, SecurityCode
from grc.utils.date_utils import convert_date_to_local_timezone
from grc.utils.logger import LogLevel, Logger

logger = Logger()


def delete_all_user_codes(email):
    delete_q = SecurityCode.__table__.delete().where(SecurityCode.email == email)
    db.session.execute(delete_q)
    db.session.commit()


def security_code_generator(email):
    delete_all_user_codes(email)

    try:
        code = ''.join(random.sample('0123456789', 5))
        record = SecurityCode(code=code, email=email)
        db.session.add(record)
        db.session.commit()
        return code

    except ValueError:
        logger.log(LogLevel.ERROR, message="Oops!  That was no valid code.  Try again...")


def is_security_code_valid(email, code, is_admin):

    if email is None:
        logger.log(LogLevel.INFO, message="No email found")
        return False

    code_record = SecurityCode.query.filter_by(code=code, email=email).first()
    valid_past_time = datetime.now() - timedelta(hours=24)

    if code_record is None:
        logger.log(LogLevel.INFO, message=f"Invalid code entered by {logger.mask_email_address(email)}")
        return False

    if valid_past_time > code_record.created:
        logger.log(LogLevel.INFO, message=f"The code has expired for {logger.mask_email_address(email)}")
        return False

    logger.log(LogLevel.INFO, message=f"The code for {logger.mask_email_address(email)} is not older than 24 hours")
    # If admin security code is still less than 24 hours old, don't remove previous code yet
    if is_admin and code_record.created > valid_past_time:
        logger.log(LogLevel.INFO, message=f"Not deleting user codes belonging to {logger.mask_email_address(email)}")
        return True

    delete_all_user_codes(email)
    return True


def generate_security_code(email):
    security_code = security_code_generator(email)
    local = convert_date_to_local_timezone(datetime.now())
    security_code_timeout = datetime.strftime(local + timedelta(hours=24), '%H:%M on %d %b %Y')
    return security_code, security_code_timeout


def send_security_code(email):
    security_code, security_code_timeout = generate_security_code(email)
    response = GovUkNotify().send_email_security_code(
        email_address=email,
        security_code=security_code,
        security_code_timeout=security_code_timeout
    )

    return response


def send_security_code_admin(email):
    security_code, expires = generate_security_code(email)

    response = GovUkNotify().send_email_admin_login_security_code(
        email_address=email,
        security_code=security_code,
        expires=expires
    )

    return response


def has_last_security_code_been_used(last_login_date: datetime, security_code_created_date: datetime):
    return last_login_date > security_code_created_date


def has_security_code_expired(security_created_date: datetime, now: datetime):
    return now > security_created_date
