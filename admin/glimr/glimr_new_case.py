from admin.glimr.glimr_register_case_api import GlimrRegisterCaseApi
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.business_logic.data_structures.partnership_details_data import PartnershipDetailsData
from grc.business_logic.data_structures.personal_details_data import PersonalDetailsData
from grc.models import Application
from typing import Dict, Any, Optional
from datetime import datetime
from grc.utils.logger import Logger, LogLevel

logger = Logger()

class GlimrNewCase:
    """
    GlimrNewCase represents a new case being registered with the GLiMR system.

    It handles extracting relevant application and personal details,
    formatting parameters, and making an API request to register the case.
    """
    def __init__(self, application: Application):
        """
        Initializes a GlimrNewCase instance with application data and details.

        :param application: The application object containing relevant case details.
        """
        self.application: Application = application
        self.application_data: ApplicationData = application.application_data()
        self.personal_details: PersonalDetailsData = self.application_data.personal_details_data
        self.partnership_details: PartnershipDetailsData = self.application_data.partnership_details_data
        self.case_reference: str | None = None

    def call_glimr_register_api(self):
        """
        Calls the GLiMR Register Case API and stores the response details.

        :raises Exception: If the API request fails.
        """
        register_api = GlimrRegisterCaseApi(self.params())
        try:
            response = register_api.call_api()
            self.case_reference = response.get("tribunalCaseNumber")
            logger.log(LogLevel.INFO, f"Successfully called GLiMR API. Responded with case reference {self.case_reference}.")
            return self

        except Exception as e:
            logger.log(LogLevel.ERROR, f"GLiMR API request failed with error {str(e)} in class {self.__class__.__name__}.")
            raise Exception(str(e))

    def params(self) -> Dict[str, Any]:
        """
        Combines and returns all necessary case parameters for the API request.
        """
        return {
                'jurisdictionId': 2000000,
                'track': 'GRP General',
                'onlineMappingCode':self.get_online_mapping_code(),
                'documentsUrl': self.application_data.documents_url(),
                **self.contact_params(),
        }

    def get_online_mapping_code(self) -> str:
        """
        Returns the online mapping code depending on the case type
        """
        if self.application_data.is_uk_application:
            return 'GRP_STANDARD'
        elif self.application_data.is_overseas_application:
            return 'GRP_OVERSEAS'
        else:
            logger.log(LogLevel.WARN, 'Unable to determine mapping code; defaulting to GRP_STANDARD.')
            return 'GRP_STANDARD'

    def contact_params(self) -> Dict[str, Any]:
        """
        Returns the contact details parameters for the API request.
        """
        return {
            'contactFirstName': self.get_first_names(),
            'contactFullName': self.get_full_name(),
            'contactSalutation': self.get_salutation(),
            'contactLastName': self.personal_details.last_name,
            'contactPreference': self.get_contact_preference(),
            'contactPhone': self.personal_details.contact_phone_number,
            'contactEmail': self.personal_details.contact_email_address,
            'contactCity': self.personal_details.address_town_city,
            'contactPostalCode': self.personal_details.address_postcode,
            'contactCountry': self.personal_details.address_country,
            **self.contact_street()
        }

    def contact_street(self) -> Dict[str, str]:
        """
        Returns the contact address details parameters for the API request.
        """
        contact_street = {'contactStreet1': self.personal_details.address_line_one}

        if self.personal_details.address_line_two:
            contact_street['contactStreet2'] = self.personal_details.address_line_two

        return contact_street

    def get_first_names(self) -> str:
        return str(self.personal_details.title) + " " + str(self.personal_details.first_name) + " " + str(self.personal_details.middle_names)

    def get_full_name(self) -> str:
        return str(self.personal_details.title) + " " + str(self.personal_details.first_name) + " " + str(self.personal_details.last_name)

    def get_salutation(self) -> str:
        return str(self.personal_details.title) + " " + str(self.personal_details.last_name)

    def get_contact_preference(self) -> Optional[str]:
        if self.personal_details.contact_email_address:
            return 'Email'
        if self.personal_details.contact_phone_number:
            return 'Phone Call'
        if self.personal_details.contact_by_post:
            return 'Post'
        return None