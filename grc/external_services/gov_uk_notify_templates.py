from flask import g

class GovUkNotifyTemplates:
    def __init__(self):

    def get_admin_login_sc_template_id():
        return 'fde1def2-bf10-45d2-8c38-2837a0a79399'

    def get_admin_forget_password_template_id():
        return 'fadf94d8-7d65-4eed-b52a-5f5b81aa32be'

    def get_admin_new_user_template_id():
        return '0ff48a4c-601e-4cc1-b6c6-30bac012c259'


    def get_feedback_template_id():
        if g.get_locale() == 'cy':
            return '388b14cd-345b-4382-9594-b8026c2242a6'
        else
            return 'd83e561e-3620-47f5-983a-4b50bf3fc33c'

    def get_docs_for_grc_app_template_id():
        if g.get_locale() == 'cy':
            return '3bcfc20d-a2ce-4132-91fa-1fc91dd1a097'
        else
            return 'a992b8c5-17e6-4dca-820c-5aa4bdd67b58'

    def get_app_recd_30_weeks_template_id():
        if g.get_locale() == 'cy':
            return '11aa2538-d411-42d8-8999-6d97c7b5f429'
        else
            return '77007bae-b688-4dbb-bc84-334b0f5d3aef'

    def get_unfinished_app_template_id():
        if g.get_locale() == 'cy':
            return '6d981947-7fa7-4c62-8912-f4324cd050ee'
        else
            return '151fce32-1f66-4efd-a875-28026e8d8d70'


    def get_security_code_template_id():
        if g.get_locale() == 'cy':
            return '1e5f89f3-44ea-4f08-8458-b4f1ef369e74'
        else
            return 'd93108b9-4a5b-4268-91ee-2bb59686e702'