from flask import g


class GovUkNotifyTemplateManager:
    # Admin
    ADMIN_LOGIN_SECURITY_CODE_TEMPLATE = 'fde1def2-bf10-45d2-8c38-2837a0a79399'
    ADMIN_FORGET_PASSWORD_TEMPLATE = '***REMOVED***'
    ADMIN_NEW_USER_TEMPLATE = '0ff48a4c-601e-4cc1-b6c6-30bac012c259'

    # GRC
    FEEDBACK_TEMPLATE = 'd83e561e-3620-47f5-983a-4b50bf3fc33c'
    DOCUMENTS_REQUIRED_TEMPLATE = 'a992b8c5-17e6-4dca-820c-5aa4bdd67b58'
    APPLICATION_RECEIVED_30_WEEKS = '77007bae-b688-4dbb-bc84-334b0f5d3aef'
    UNFINISHED_APPLICATION = '151fce32-1f66-4efd-a875-28026e8d8d70'
    SECURITY_CODE_LOGIN = 'd93108b9-4a5b-4268-91ee-2bb59686e702'

    def __init__(self, flask_app):
        if flask_app == 'grc' and g.lang_code == 'cy':
            self.FEEDBACK_TEMPLATE = '388b14cd-345b-4382-9594-b8026c2242a6'
            self.DOCUMENTS_REQUIRED_TEMPLATE = '3bcfc20d-a2ce-4132-91fa-1fc91dd1a097'
            self.APPLICATION_RECEIVED_30_WEEKS = '11aa2538-d411-42d8-8999-6d97c7b5f429'
            self.UNFINISHED_APPLICATION = '6d981947-7fa7-4c62-8912-f4324cd050ee'
            self.SECURITY_CODE_LOGIN = '1e5f89f3-44ea-4f08-8458-b4f1ef369e74'
