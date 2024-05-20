from flask import current_app
from notifications_python_client.notifications import NotificationsAPIClient
from notifications_python_client.errors import HTTPError
from grc.external_services.gov_uk_notify_templates import GovUkNotifyTemplates
from grc.utils.security_code import generate_security_code_and_expiry
from grc.utils.logger import LogLevel, Logger
from werkzeug.exceptions import HTTPException

logger = Logger()


class GovUkNotify:
    def __init__(self):
        gov_uk_notify_api_key = current_app.config['NOTIFY_API']
        self.space = current_app.config.get('ENVIRONMENT', 'local')
        self.is_production = self.space == 'production'
        self.notify_override_email = current_app.config['NOTIFY_OVERRIDE_EMAIL']
        self.gov_uk_notify_client = NotificationsAPIClient(gov_uk_notify_api_key)
        self.templateHelper = GovUkNotifyTemplates()

    def send_email_security_code(self, email_address: str):
        security_code, security_code_timeout = generate_security_code_and_expiry(email_address)
        personalisation = {
            'security_code': security_code,
            'security_code_timeout': security_code_timeout,
        }

        return self.send_email(
            email_address=email_address,
            template_id=self.templateHelper.get_security_code_template_id(),
            personalisation=personalisation
        )

    def send_email_unfinished_application(self, email_address: str, expiry_days: str):
        personalisation = {
            'expiry_days': expiry_days,
        }

        return self.send_email(
            email_address=email_address,
            template_id=self.templateHelper.get_unfinished_app_template_id(),
            personalisation=personalisation
        )

    def send_email_completed_application(self, email_address: str, documents_to_be_posted: str):
        personalisation = {
            'documents_to_be_posted': documents_to_be_posted,
        }

        return self.send_email(
            email_address=email_address,
            template_id=self.templateHelper.get_app_recd_30_weeks_template_id(),
            personalisation=personalisation
        )

    def send_email_documents_you_need_for_your_grc_application(self, email_address: str, documents_required: dict):
        return self.send_email(
            email_address=email_address,
            template_id=self.templateHelper.get_docs_for_grc_app_template_id(),
            personalisation=documents_required
        )

    def send_email_feedback(
            self,
            how_easy_to_complete_application: str,
            any_questions_difficult_to_answer: str,
            which_questions_difficult_to_answer: str,
            needed_to_call_admin_team: str,
            what_did_you_need_help_with: str,
            used_doc_checker: str,
            experience_of_using_doc_checker: str,
            any_other_suggestions: str
    ):
        personalisation = {
            'how_easy_to_complete_application': how_easy_to_complete_application,
            'any_questions_difficult_to_answer': any_questions_difficult_to_answer,
            'which_questions_difficult_to_answer': which_questions_difficult_to_answer,
            'needed_to_call_admin_team': needed_to_call_admin_team,
            'what_did_you_need_help_with': what_did_you_need_help_with,
            'used_doc_checker': used_doc_checker,
            'experience_of_using_doc_checker': experience_of_using_doc_checker,
            'any_other_suggestions': any_other_suggestions,
        }

        return self.send_email(
            email_address='grc-service-feedback@cabinetoffice.gov.uk',
            template_id=self.templateHelper.get_feedback_template_id(),
            personalisation=personalisation
        )

    def send_email_admin_login_security_code(self, email_address: str):
        security_code, expires = generate_security_code_and_expiry(email_address)
        personalisation = {
            'expires': expires,
            'security_code': security_code,
        }

        return self.send_email(
            email_address=email_address,
            template_id=self.templateHelper.get_admin_login_sc_template_id(),
            personalisation=personalisation
        )

    def send_email_admin_forgot_password(self, email_address: str):
        security_code, expires = generate_security_code_and_expiry(email_address)
        personalisation = {
            'expires': expires,
            'security_code': security_code,
        }

        return self.send_email(
            email_address=email_address,
            template_id=self.templateHelper.get_admin_forget_password_template_id(),
            personalisation=personalisation
        )

    def send_email_admin_new_user(self, email_address: str, temporary_password: str, application_link: str):
        personalisation = {
            'temporary_password': temporary_password,
            'application_link': application_link,
        }

        return self.send_email(
            email_address=email_address,
            template_id=self.templateHelper.get_admin_new_user_template_id(),
            personalisation=personalisation
        )

    def send_email(self, email_address: str, template_id: str, personalisation: dict):
        if personalisation is None:
            personalisation = {}

        if self.is_production:
            personalisation['environment_and_email_address'] = ''
        else:
            personalisation['environment_and_email_address'] = f"[{self.space} to:{email_address}] "
            if self.notify_override_email:
                email_address = self.notify_override_email

        try:
            response = self.gov_uk_notify_client.send_email_notification(
                email_address=email_address,
                template_id=template_id,
                personalisation=personalisation
            )
            return response

        except HTTPError as error:
            message = (f'Error sending email to user - {logger.mask_email_address(email_address)}: {error.status_code}'
                       f' - {error.message}')
            logger.log(LogLevel.ERROR, message=message)
            raise GovUkNotifyException(error.status_code, message)


class GovUkNotifyException(HTTPException):
    def __init__(self, error_code, message=None):
        self.code = error_code
        self.default_message = 'Error sending email notification via notify'
        self.description = message if message else self.default_message
