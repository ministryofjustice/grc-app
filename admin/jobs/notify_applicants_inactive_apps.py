from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint
from flask.cli import with_appcontext
from sqlalchemy.sql import extract, not_
from grc.external_services.gov_uk_notify import GovUkNotify
from grc.models import Application, ApplicationStatus

notify_applicants_inactive_apps = Blueprint('notify_applicants_inactive_apps', __name__)


def send_reminder_emails_before_application_deletion():
    days_between_last_update_and_deletion = 183

    deletion_reminder_days_and_phrases = {
        # days: 'phrase'
        90: '3 months',
        30: '1 month',
        7: '1 week',
    }

    for days_to_send_reminder, time_phrase in deletion_reminder_days_and_phrases.items():

        print(f'Sending reminder emails to applications {time_phrase} from being deleted', flush=True)

        today = datetime.today()
        last_updated_date = calculate_last_updated_date(today, days_to_send_reminder, days_between_last_update_and_deletion)

        applications_to_remind = Application.query.filter(
            Application.status == ApplicationStatus.STARTED,
            extract('day', Application.updated) == last_updated_date.day,
            extract('month', Application.updated) == last_updated_date.month,
            extract('year', Application.updated) == last_updated_date.year
        )

        print(f'Sending reminder emails to {applications_to_remind.count()} applications', flush=True)
        email_send_count = 0
        for application_to_remind in applications_to_remind.all():
            existing_application = Application.query.filter(
                Application.email == application_to_remind.email,
                ((Application.status == ApplicationStatus.SUBMITTED) | (Application.status == ApplicationStatus.DOWNLOADED) | (Application.status == ApplicationStatus.COMPLETED))
            ).first()
            if existing_application is None:
                GovUkNotify().send_email_unfinished_application(
                    email_address=application_to_remind.email,
                    expiry_days=time_phrase
                )
                email_send_count += 1
        print(f'Send {email_send_count} emails\n', flush=True)

    return 200


def calculate_last_updated_date(today, days_to_send_reminder_before_deletion, days_between_last_update_and_deletion):
    return today - relativedelta(days=(days_between_last_update_and_deletion - days_to_send_reminder_before_deletion))


@notify_applicants_inactive_apps.cli.command('run')
@with_appcontext
def main():
    try:
        print('running notify applicants inactive apps job', flush=True)
        applicants_notified = send_reminder_emails_before_application_deletion()
        assert applicants_notified == 200
        print('finished notify applicants inactive apps job', flush=True)
    except Exception as e:
        print(f'Error notifying applicants cron, message = {e}', flush=True)


if __name__ == '__main__':
    main()
