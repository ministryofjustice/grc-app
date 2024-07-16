from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint
from flask.cli import with_appcontext
from sqlalchemy.sql import extract
from grc.external_services.gov_uk_notify import GovUkNotify
from grc.models import db, Application, ApplicationStatus, SecurityCode
from grc.utils.application_files import ApplicationFiles

notify_applicants_inactive_apps = Blueprint('notify_applicants_inactive_apps', __name__)


def application_notifications():
    days_between_last_update_and_deletion = 183  # approximately 6 months
    abandon_application_after_period_of_inactivity(days_between_last_update_and_deletion)
    send_reminder_emails_before_application_deletion(days_between_last_update_and_deletion)
    delete_completed_applications()
    delete_expired_security_codes()

    return 200


def abandon_application_after_period_of_inactivity(days_between_last_update_and_deletion):
    print(f'\nAbandoning applications {days_between_last_update_and_deletion} days from last update\n', flush=True)
    now = datetime.now()
    earliest_allowed_inactive_application_updated_date = calculate_earliest_allowed_inactive_application_updated_date(now, days_between_last_update_and_deletion)

    applications_to_anonymise = Application.query.filter(
        Application.status == ApplicationStatus.STARTED,
        Application.updated < earliest_allowed_inactive_application_updated_date
    )

    print(f'Anonymising {applications_to_anonymise.count()} inactive applications', flush=True)
    for application_to_anonymise in applications_to_anonymise.all():
        anonymise_application(application_to_anonymise, new_state=ApplicationStatus.ABANDONED)

    db.session.commit()


def calculate_earliest_allowed_inactive_application_updated_date(now, days_between_last_update_and_deletion):
    return now - relativedelta(days=days_between_last_update_and_deletion)


def send_reminder_emails_before_application_deletion(days_between_last_update_and_deletion):
    deletion_reminder_days_and_phrases = {
        # days: 'phrase'
        90: '3 months',
        30: '1 month',
        7: '1 week',
    }

    for days_to_send_reminder, time_phrase in deletion_reminder_days_and_phrases.items():

        print(f'Sending reminder emails to applications {time_phrase} from being deleted\n',
              flush=True)

        today = datetime.today()
        last_updated_date = calculate_last_updated_date(today, days_to_send_reminder, days_between_last_update_and_deletion)

        applications_to_remind = Application.query.filter(
            Application.status == ApplicationStatus.STARTED,
            extract('day', Application.updated) == last_updated_date.day,
            extract('month', Application.updated) == last_updated_date.month,
            extract('year', Application.updated) == last_updated_date.year
        ).all()

        for application_to_remind in applications_to_remind:
            existing_application = Application.query.filter(
                Application.email == application_to_remind.email,
                ((Application.status == ApplicationStatus.SUBMITTED) | (Application.status == ApplicationStatus.DOWNLOADED) | (Application.status == ApplicationStatus.COMPLETED))
            ).first()
            if existing_application is None:
                GovUkNotify().send_email_unfinished_application(
                    email_address=application_to_remind.email,
                    expiry_days=time_phrase
                )


def calculate_last_updated_date(today, days_to_send_reminder_before_deletion, days_between_last_update_and_deletion):
    return today - relativedelta(days=(days_between_last_update_and_deletion - days_to_send_reminder_before_deletion))


def delete_completed_applications():
    print(f'\nDeleting completed applications', flush=True)
    days_between_application_completion_and_anonymisation = 7

    now = datetime.now()
    earliest_allowed_application_completed_date = calculate_earliest_allowed_application_completed_date(now, days_between_application_completion_and_anonymisation)

    applications_to_anonymise = Application.query.filter(
        Application.status == ApplicationStatus.COMPLETED,
        Application.completed < earliest_allowed_application_completed_date
    )
    all_applications_to_anonymise = applications_to_anonymise.all()
    if all_applications_to_anonymise:
        print(f'Deleting {applications_to_anonymise.count()} completed applications\n', flush=True)
        for application_to_anonymise in all_applications_to_anonymise:
            anonymise_application(application_to_anonymise, new_state=ApplicationStatus.DELETED)
        db.session.commit()


def calculate_earliest_allowed_application_completed_date(now, days_between_application_completion_and_anonymisation):
    return now - relativedelta(days=days_between_application_completion_and_anonymisation)


def anonymise_application(application_to_anonymise, new_state: ApplicationStatus):
    if not application_to_anonymise:
        return

    try:
        ApplicationFiles().delete_application_files(
            application_to_anonymise.reference_number,
            application_to_anonymise.application_data(),
        )
    except Exception as e:
        print(f'Error deleting application application files - {e}', flush=True)
    finally:
        application_to_anonymise.email = ''
        application_to_anonymise.user_input = ''
        application_to_anonymise.status = new_state


def delete_expired_security_codes():
    print(f'\nDeleting expired security codes', flush=True)
    hours_between_security_code_creation_and_expiry = 24

    now = datetime.now()
    earliest_allowed_security_code_creation_time = calculate_earliest_allowed_security_code_creation_time(now, hours_between_security_code_creation_and_expiry)

    security_codes_to_delete = SecurityCode.query.filter(
        SecurityCode.created < earliest_allowed_security_code_creation_time
    )

    print(f'Deleting {security_codes_to_delete.count()} expired security codes\n', flush=True)

    for security_code_to_delete in security_codes_to_delete:
        db.session.delete(security_code_to_delete)

    db.session.commit()


def calculate_earliest_allowed_security_code_creation_time(now, hours_between_security_code_creation_and_expiry):
    return now - relativedelta(hours=hours_between_security_code_creation_and_expiry)


@notify_applicants_inactive_apps.cli.command('run')
@with_appcontext
def main():
    try:
        print('running notify applicants inactive apps job', flush=True)
        applicants_notified = application_notifications()
        assert applicants_notified == 200
        print('finished notify applicants inactive apps job', flush=True)
    except Exception as e:
        print(f'Error notifying applicants cron, message = {e}', flush=True)


if __name__ == '__main__':
    main()
