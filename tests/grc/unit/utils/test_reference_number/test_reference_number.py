from grc.utils import reference_number as rf


class TestReferenceNumber:
    def test_reference_number_string(self):
        reference_number = 'D4OVT4GG'
        assert rf.reference_number_string(reference_number) == 'D4OV-T4GG'

    def test_reference_number_string_with_spaces(self):
        reference_number = 'D 4O VT 4    G G'
        assert rf.reference_number_string(reference_number) == 'D4OV-T4GG'

    def test_reference_number_string_with_dashes(self):
        reference_number = 'D4-OV-T4-GG-'
        assert rf.reference_number_string(reference_number) == 'D4OV-T4GG'

    def test_reference_number_string_lowercase(self):
        reference_number = 'd4OVT4gG'
        assert rf.reference_number_string(reference_number) == 'D4OV-T4GG'

    def test_reference_number_is_valid_public_user(self,  test_application):
        assert rf.reference_number_is_valid(test_application.reference_number, test_application.email) is True

    def test_reference_number_is_invalid_public_user(self, app, test_application):
        with app.test_request_context():
            assert rf.reference_number_is_valid('INVALID-REF', test_application.email) is False

    def test_reference_number_is_valid_submitted_admin(self, app, test_submitted_application):
        with app.test_request_context():
            assert rf.reference_number_is_valid_admin(test_submitted_application.reference_number) is True

    def test_reference_number_is_valid_downloaded_admin(self, app, test_downloaded_application):
        with app.test_request_context():
            assert rf.reference_number_is_valid_admin(test_downloaded_application.reference_number) is True

    def test_reference_number_is_valid_completed_admin(self, app, test_completed_application):
        with app.test_request_context():
            assert rf.reference_number_is_valid_admin(test_completed_application.reference_number) is True

    def test_reference_number_is_invalid_admin(self, app, test_application):
        with app.test_request_context():
            assert rf.reference_number_is_valid_admin('INVALID-REF') is False

    def test_reference_number_is_invalid_not_submitted_admin(self, app, test_application):
        with app.test_request_context():
            assert rf.reference_number_is_valid_admin(test_application.reference_number) is False
