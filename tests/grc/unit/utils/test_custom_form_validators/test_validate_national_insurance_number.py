import pytest
from grc.personal_details.forms import HmrcForm
from grc.utils.form_custom_validators import validateNationalInsuranceNumber
from wtforms.validators import ValidationError


class TestValidateNationalInsuranceNumber:

    def test_validate_national_insurance_number_valid_numbers(self, app):
        with app.app_context():
            form = HmrcForm()
            valid_ni_numbers = ['PP 12 34 56 A', 'PP123456A', 'AZ 8 237 23C', 'KW728462 D']
            for number in valid_ni_numbers:
                form.national_insurance_number.data = number
                assert validateNationalInsuranceNumber(form, form.national_insurance_number) is None

    def test_validate_national_insurance_number_valid_numbers_lowercase(self, app):
        with app.app_context():
            form = HmrcForm()
            valid_ni_numbers = ['pp 12 34 56 a', 'pp123456a', 'az 8 237 23c', 'kw728462 d']
            for number in valid_ni_numbers:
                form.national_insurance_number.data = number
                assert validateNationalInsuranceNumber(form, form.national_insurance_number) is None

    def test_validate_national_insurance_number_invalid_first_letter(self, app):
        with app.app_context():
            form = HmrcForm()
            invalid_ni_numbers = ['DP123456A', 'FP123456A', 'IP123456A', 'QP123456A', 'UP123456A', 'VP123456A']
            for number in invalid_ni_numbers:
                form.national_insurance_number.data = number
                with pytest.raises(ValidationError, match='Enter a valid National Insurance number'):
                    validateNationalInsuranceNumber(form, form.national_insurance_number)

    def test_validate_national_insurance_number_invalid_prefix_combinations(self, app):
        with app.app_context():
            form = HmrcForm()
            invalid_ni_numbers = ['BG123456A', 'GB123456A', 'KN123456A', 'NK123456A', 'NT123456A', 'TN123456A',
                                  'ZZ123456A']
            form.national_insurance_number.data = invalid_ni_numbers
            for number in invalid_ni_numbers:
                form.national_insurance_number.data = number
                with pytest.raises(ValidationError, match='Enter a valid National Insurance number'):
                    validateNationalInsuranceNumber(form, form.national_insurance_number)

    def test_validate_national_insurance_number_invalid_number_length(self, app):
        with app.app_context():
            form = HmrcForm()
            invalid_ni_numbers = ['PP12354325456A', 'PP1234533456A', 'PP126A', 'PP123443253556A', 'PP1354235465623456A']
            form.national_insurance_number.data = invalid_ni_numbers
            for number in invalid_ni_numbers:
                form.national_insurance_number.data = number
                with pytest.raises(ValidationError, match='Enter a valid National Insurance number'):
                    validateNationalInsuranceNumber(form, form.national_insurance_number)

    def test_validate_national_insurance_number_invalid_suffix(self, app):
        with app.app_context():
            form = HmrcForm()
            invalid_ni_numbers = ['PP 12 34 56 E', 'PP123456f', 'AZ 8 237 23G', 'KW728462 H']
            form.national_insurance_number.data = invalid_ni_numbers
            for number in invalid_ni_numbers:
                form.national_insurance_number.data = number
                with pytest.raises(ValidationError, match='Enter a valid National Insurance number'):
                    validateNationalInsuranceNumber(form, form.national_insurance_number)

