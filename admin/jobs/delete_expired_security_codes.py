from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint
from flask.cli import with_appcontext
from grc.models import db, SecurityCode
from grc.utils.logger import LogLevel, Logger

logger = Logger()
delete_expired_security_codes = Blueprint('delete_expired_security_codes', __name__)


def delete_security_codes():
    logger.log(LogLevel.WARN, f'\nDeleting expired security codes')
    hours_between_security_code_creation_and_expiry = 24

    now = datetime.now()
    earliest_allowed_security_code_creation_time = calculate_earliest_allowed_security_code_creation_time(now, hours_between_security_code_creation_and_expiry)

    security_codes_to_delete = SecurityCode.query.filter(
        SecurityCode.created < earliest_allowed_security_code_creation_time
    )

    logger.log(LogLevel.WARN, f'Deleting {security_codes_to_delete.count()} expired security codes\n')

    for security_code_to_delete in security_codes_to_delete:
        db.session.delete(security_code_to_delete)

    db.session.commit()

    return 200


def calculate_earliest_allowed_security_code_creation_time(now, hours_between_security_code_creation_and_expiry):
    return now - relativedelta(hours=hours_between_security_code_creation_and_expiry)


@delete_expired_security_codes.cli.command('run')
@with_appcontext
def main():
    try:
        logger.log(LogLevel.WARN, 'running delete expired security codes job')
        security_codes_deleted = delete_security_codes()
        assert security_codes_deleted == 200
        logger.log(LogLevel.INFO, 'finished delete expired security codes job')
    except Exception as e:
        logger.log(LogLevel.ERROR, f'Error delete expired security codes cron, message = {e}')


if __name__ == '__main__':
    main()
