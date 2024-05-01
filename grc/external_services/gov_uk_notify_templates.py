from flask import g

class GovUkNotifyTemplates:
    def __init__(self):

    def get_admin_login_sc_template_id():
        if g.get_locale() == 'cy':
            return 'unknown'
        else
            return 'fde1def2-bf10-45d2-8c38-2837a0a79399'

    def get_admin_forget_password_template_id():
        if g.get_locale() == 'cy':
            return 'unknown'
        else
            return 'fadf94d8-7d65-4eed-b52a-5f5b81aa32be'

    def get_admin_new_user_template_id():
        if g.get_locale() == 'cy':
            return 'unknown'
        else
            return '0ff48a4c-601e-4cc1-b6c6-30bac012c259'


    def get_feedback_template_id():
        if g.get_locale() == 'cy':
            return 'unknown'
        else
            return 'd83e561e-3620-47f5-983a-4b50bf3fc33c'

    def get_docs_for_grc_app_template_id():
        if g.get_locale() == 'cy':
            return 'unknown'
        else
            return 'a992b8c5-17e6-4dca-820c-5aa4bdd67b58'

    def get_app_recd_30_weeks_template_id():
        if g.get_locale() == 'cy':
            return 'unknown'
        else
            return '77007bae-b688-4dbb-bc84-334b0f5d3aef'

    def get_unfinished_app_template_id():
        if g.get_locale() == 'cy':
            return 'unknown'
        else
            return '151fce32-1f66-4efd-a875-28026e8d8d70'


    def get_security_code_template_id():
        if g.get_locale() == 'cy':
            return 'unknown'
        else
            return 'd93108b9-4a5b-4268-91ee-2bb59686e702'