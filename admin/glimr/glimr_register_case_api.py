from .glimr_client_api import GlimrClientApi

class GlimrRegisterCaseApi(GlimrClientApi):
    def endpoint(self) -> str:
        return 'registernewcase'
