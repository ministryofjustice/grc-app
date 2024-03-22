from grc.utils.reference_number import reference_number_string, reference_number_is_valid


class TestReferenceNumber:
    def test_reference_number_string(self):
        reference_number = 'D4OVT4GG'
        assert reference_number_string(reference_number) == 'D4OV-T4GG'

    def test_reference_number_string_with_spaces(self):
        reference_number = 'D 4O VT 4    G G'
        assert reference_number_string(reference_number) == 'D4OV-T4GG'

    def test_reference_number_string_with_dashes(self):
        reference_number = 'D4-OV-T4-GG-'
        assert reference_number_string(reference_number) == 'D4OV-T4GG'

    def test_reference_number_string_lowercase(self):
        reference_number = 'd4OVT4gG'
        assert reference_number_string(reference_number) == 'D4OV-T4GG'

    def test_reference_number_is_valid_public_user(self,  test_application):
        assert reference_number_is_valid(test_application.reference_number, test_application.email, False) is True

    def test_reference_number_is_invalid_public_user(self, app, test_application):
        with app.test_request_context():
            assert reference_number_is_valid('INVALID-REF', test_application.email, False) is False

    def test_reference_number_is_valid_admin_user(self, app, test_application):
        with app.test_request_context():
            assert reference_number_is_valid(test_application.reference_number, None, True) is True

    def test_reference_number_is_invalid_admin_user(self, app, test_application):
        with app.test_request_context():
            assert reference_number_is_valid('INVALID-REF', None, True) is False
