import pytest
from grc.submit_and_pay.forms import HelpTypeForm
from grc.utils.form_custom_validators import validate_hwf_reference_number
from wtforms.validators import ValidationError


class TestValidateHWFReferenceNumber:

    def test_validate_hwf_reference_number_valid_numbers(self, app):
        with app.app_context():
            form = HelpTypeForm()
            form.how_applying_for_fees.data = 'USING_ONLINE_SERVICE'
            valid_hwf_numbers = ['HWF-123-ABC', 'HWF123ABC', 'HWF-ABC-123', 'HWF1A2B3C']
            for number in valid_hwf_numbers:
                form.help_with_fees_reference_number.data = number
                assert validate_hwf_reference_number(form, form.help_with_fees_reference_number) is None

    def test_validate_hwf_reference_number_invalid_numbers(self, app):
        with app.app_context():
            form = HelpTypeForm()
            form.how_applying_for_fees.data = 'USING_ONLINE_SERVICE'
            invalid_hwf_numbers = ['HWF-123ABC', 'hwf123ABC', 'HWFABC-123', 'HWF1A2B3C-', 'HWF-ABC-123-DE4',
                                   'ABC123DEF']
            for number in invalid_hwf_numbers:
                form.help_with_fees_reference_number.data = number
                with pytest.raises(ValidationError, match='Enter a valid \'Help with fees\' reference number'):
                    validate_hwf_reference_number(form, form.help_with_fees_reference_number)