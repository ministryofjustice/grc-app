from flask import current_app
from notifications_python_client.notifications import NotificationsAPIClient
from grc.external_services.gov_uk_notify_templates import GovUkNotifyTemplates


class GovUkNotify:
    def __init__(self):
        gov_uk_notify_api_key = current_app.config['NOTIFY_API']
        self.space = current_app.config.get('ENVIRONMENT', 'local')
        self.is_production = self.space == 'production'
        self.notify_override_email = current_app.config['NOTIFY_OVERRIDE_EMAIL']
        self.gov_uk_notify_client = NotificationsAPIClient(gov_uk_notify_api_key)

    def send_email_security_code(self, email_address: str, security_code: str, security_code_timeout: str):
        personalisation = {
            'security_code': security_code,
            'security_code_timeout': security_code_timeout,
        }

        return self.send_email(
            email_address=email_address,
            template_id=get_security_code_template_id,
            personalisation=personalisation
        )

    def send_email_unfinished_application(self, email_address: str, expiry_days: str, grc_return_link: str):
        personalisation = {
            'expiry_days': expiry_days,
            'grc_return_link': grc_return_link,
        }

        return self.send_email(
            email_address=email_address,
            template_id=get_unfinished_app_template_id,
            personalisation=personalisation
        )

    def send_email_completed_application(self, email_address: str, documents_to_be_posted: str):
        personalisation = {
            'documents_to_be_posted': documents_to_be_posted,
        }

        return self.send_email(
            email_address=email_address,
            template_id=get_app_recd_30_weeks_template_id,
            personalisation=personalisation
        )

    def send_email_documents_you_need_for_your_grc_application(self, email_address: str, documents_required: dict):
        return self.send_email(
            email_address=email_address,
            template_id=get_docs_for_grc_app_template_id,
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
            template_id=get_feedback_template_id,
            personalisation=personalisation
        )

    def send_email_admin_login_security_code(self, email_address: str, expires: str, security_code: str):
        personalisation = {
            'expires': expires,
            'security_code': security_code,
        }

        return self.send_email(
            email_address=email_address,
            template_id=get_admin_login_sc_template_id,
            personalisation=personalisation
        )

    def send_email_admin_forgot_password(self, email_address: str, expires: str, security_code: str):
        personalisation = {
            'expires': expires,
            'security_code': security_code,
        }

        return self.send_email(
            email_address=email_address,
            template_id=get_admin_forget_password_template_id,
            personalisation=personalisation
        )

    def send_email_admin_new_user(self, email_address: str, temporary_password: str, application_link: str):
        personalisation = {
            'temporary_password': temporary_password,
            'application_link': application_link,
        }

        return self.send_email(
            email_address=email_address,
            template_id=get_admin_new_user_template_id,
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

        response = self.gov_uk_notify_client.send_email_notification(
            email_address=email_address,
            template_id=template_id,
            personalisation=personalisation
        )

        return response
