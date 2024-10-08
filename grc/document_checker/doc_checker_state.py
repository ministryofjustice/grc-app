from enum import Enum, auto


class GrcEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class CurrentlyInAPartnershipEnum(GrcEnum):
    MARRIED = auto()
    CIVIL_PARTNERSHIP = auto()
    NEITHER = auto()


class DocCheckerState(object):
    changed_name_to_reflect_gender: bool = None
    currently_in_a_partnership: CurrentlyInAPartnershipEnum = None
    previous_partnership_partner_died: bool = None
    previous_partnership_ended: bool = None
    plan_to_remain_in_a_partnership: bool = None
    gender_recognition_outside_uk: bool = None

    @classmethod
    def _get_list_of_documents_required_methods(cls):
        return [prop for prop in dir(cls) if
                prop.startswith('need_to_send_') and isinstance(getattr(cls, prop, None), property)]

    def get_list_of_documents_required_values(self):
        return {name: getattr(self, name) for name in self._get_list_of_documents_required_methods()}

    @property
    def is_married(self) -> bool:
        return self.currently_in_a_partnership == CurrentlyInAPartnershipEnum.MARRIED

    @property
    def is_in_civil_partnership(self) -> bool:
        return self.currently_in_a_partnership == CurrentlyInAPartnershipEnum.CIVIL_PARTNERSHIP

    @property
    def is_currently_in_partnership(self) -> bool:
        return self.is_married or self.is_in_civil_partnership

    @property
    def is_not_in_partnership(self) -> bool:
        return not self.is_currently_in_partnership

    @property
    def need_to_send_name_change_documents(self) -> bool:
        return self.changed_name_to_reflect_gender

    @property
    def need_to_send_medical_reports(self) -> bool:
        return not self.gender_recognition_outside_uk

    @property
    def need_to_send_evidence_of_living_in_gender(self) -> bool:
        return not self.gender_recognition_outside_uk

    @property
    def need_to_send_statutory_declaration_for_single_applicant(self) -> bool:
        return self.is_not_in_partnership

    @property
    def need_to_send_statutory_declaration_for_applicant_in_partnership(self) -> bool:
        return self.is_currently_in_partnership

    @property
    def need_to_send_partners_statutory_declaration(self) -> bool:
        return self.is_currently_in_partnership and self.plan_to_remain_in_a_partnership

    @property
    def need_to_send_partnership_certificate(self) -> bool:
        return self.is_currently_in_partnership

    @property
    def need_to_send_death_certificate(self) -> bool:
        return self.is_not_in_partnership and self.previous_partnership_partner_died

    @property
    def need_to_send_decree_absolute(self) -> bool:
        return self.is_not_in_partnership and self.previous_partnership_ended

    @property
    def need_to_send_proof_gender_recognised_outside_uk(self) -> bool:
        return self.gender_recognition_outside_uk

    @property
    def need_to_send_statutory_declaration_for_married_applicant(self):
        return self.is_married and self.need_to_send_statutory_declaration_for_applicant_in_partnership

    @property
    def need_to_send_statutory_declaration_for_applicant_in_civil_partnership(self):
        return self.is_in_civil_partnership and self.need_to_send_statutory_declaration_for_applicant_in_partnership

    @property
    def need_to_send_spouses_statutory_declaration(self):
        return self.is_married and self.need_to_send_partners_statutory_declaration

    @property
    def need_to_send_civil_partners_statutory_declaration(self):
        return self.is_in_civil_partnership and self.need_to_send_partners_statutory_declaration

    @property
    def need_to_send_marriage_certificate(self):
        return self.is_married and self.need_to_send_partnership_certificate

    @property
    def need_to_send_civil_partnership_certificate(self):
        return self.is_in_civil_partnership and self.need_to_send_partnership_certificate
