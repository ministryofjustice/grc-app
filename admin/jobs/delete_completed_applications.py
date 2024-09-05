from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint
from flask.cli import with_appcontext
from grc.models import db, Application, ApplicationStatus
from grc.utils.application_files import ApplicationFiles

delete_completed_applications = Blueprint('delete_completed_applications', __name__)


def mark_applications_as_deleted():
    print(f'\nDeleting completed applications', flush=True)
    days_between_application_completion_and_anonymisation = 7

    now = datetime.now()
    earliest_allowed_application_completed_date = calculate_earliest_allowed_application_completed_date(now, days_between_application_completion_and_anonymisation)

    applications_to_delete = Application.query.filter(
        Application.status == ApplicationStatus.COMPLETED,
        Application.completed < earliest_allowed_application_completed_date
    )
    print(f'Deleting {applications_to_delete.count()} completed applications\n', flush=True)
    all_applications_to_delete = applications_to_delete.all()
    for application_to_delete in all_applications_to_delete:
        delete_application(application_to_delete)
    db.session.commit()

    return 200


def calculate_earliest_allowed_application_completed_date(now, days_between_application_completion_and_anonymisation):
    return now - relativedelta(days=days_between_application_completion_and_anonymisation)


def delete_application(application_to_delete):
    if not application_to_delete:
        return

    try:
        data = application_to_delete.application_data()
    except Exception as e:
        print(f'Error getting application data for {application_to_delete.reference_number} - {e}', flush=True)
        data = None

    try:
        if data:
            ApplicationFiles().delete_application_files(
                application_to_delete.reference_number,
                data,
            )

            application_to_delete.email = ''
            application_to_delete.user_input = ''
    except Exception as e:
        print(f'Error deleting application files for {application_to_delete.reference_number} - {e}', flush=True)
    finally:
        application_to_delete.status = ApplicationStatus.DELETED


@delete_completed_applications.cli.command('run')
@with_appcontext
def main():
    try:
        print('running delete completed apps job', flush=True)
        applications_deleted = mark_applications_as_deleted()
        assert applications_deleted == 200
        print('finished delete completed apps job', flush=True)
    except Exception as e:
        logger.log(LogLevel.ERROR, f'Error delete completed apps cron, message = {e}')


if __name__ == '__main__':
    main()
