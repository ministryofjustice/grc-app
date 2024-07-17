from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint
from flask.cli import with_appcontext
from grc.models import db, Application, ApplicationStatus
from grc.utils.application_files import ApplicationFiles

anonymise_expired_applications = Blueprint('anonymise_expired_applications', __name__)


def abandon_application_after_period_of_inactivity():
    days_between_last_update_and_deletion = 183  # approximately 6 months
    print(f'\nAbandoning applications {days_between_last_update_and_deletion} days from last update\n', flush=True)

    now = datetime.now()
    earliest_allowed_inactive_application_updated_date = calculate_earliest_allowed_inactive_application_updated_date(now, days_between_last_update_and_deletion)

    applications_to_anonymise = Application.query.filter(
        Application.status == ApplicationStatus.STARTED,
        Application.updated < earliest_allowed_inactive_application_updated_date
    )

    print(f'Anonymising {applications_to_anonymise.count()} inactive applications', flush=True)
    for application_to_anonymise in applications_to_anonymise.all():
        anonymise_application(application_to_anonymise)

    db.session.commit()

    return 200


def calculate_earliest_allowed_inactive_application_updated_date(now, days_between_last_update_and_deletion):
    return now - relativedelta(days=days_between_last_update_and_deletion)


def anonymise_application(application_to_anonymise):
    if not application_to_anonymise:
        return


    try:
        data = application_to_anonymise.application_data()
    except Exception as e:
        print(f'Error getting application data for {application_to_anonymise.reference_number} - {e}', flush=True)
        data = None

    try:
        if data:
            ApplicationFiles().delete_application_files(
                application_to_anonymise.reference_number,
                data,
            )

            application_to_anonymise.email = ''
            application_to_anonymise.user_input = ''
    except Exception as e:
        print(f'Error deleting application files for {application_to_anonymise.reference_number} - {e}', flush=True)
    finally:
        application_to_anonymise.status = ApplicationStatus.ABANDONED


@anonymise_expired_applications.cli.command('run')
@with_appcontext
def main():
    try:
        print('running anonymise expired applications job', flush=True)
        anonymised_applications = abandon_application_after_period_of_inactivity()
        assert anonymised_applications == 200
        print('finished anonymise expired applications job', flush=True)
    except Exception as e:
        print(f'Error anonymise expired applications cron, message = {e}', flush=True)


if __name__ == '__main__':
    main()
