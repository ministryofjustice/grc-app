from admin.glimr.glimr_new_case import GlimrNewCase
from grc.business_logic.data_structures.personal_details_data import PersonalDetailsData


def _glimr_case_for(personal_details: PersonalDetailsData) -> GlimrNewCase:
    case = GlimrNewCase.__new__(GlimrNewCase)
    case.personal_details = personal_details
    return case


class TestGlimrContactPreference:

    def test_email_address_presence_alone_does_not_force_email_preference(self):
        personal_details = PersonalDetailsData()
        personal_details.contact_email_address = 'alex.example@example.com'
        personal_details.contact_by_email = False
        personal_details.contact_phone_number = '07123456789'

        case = _glimr_case_for(personal_details)

        assert case.get_contact_preference() == 'Phone Call'

    def test_email_preference_returned_when_chosen(self):
        personal_details = PersonalDetailsData()
        personal_details.contact_email_address = 'alex.example@example.com'
        personal_details.contact_by_email = True

        case = _glimr_case_for(personal_details)

        assert case.get_contact_preference() == 'Email'

    def test_post_preference_returned_when_only_post_chosen(self):
        personal_details = PersonalDetailsData()
        personal_details.contact_email_address = 'alex.example@example.com'
        personal_details.contact_by_email = False
        personal_details.contact_phone_number = ''
        personal_details.contact_by_post = True

        case = _glimr_case_for(personal_details)

        assert case.get_contact_preference() == 'Post'
