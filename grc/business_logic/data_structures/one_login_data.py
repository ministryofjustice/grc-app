import datetime
from typing import Optional, List
from grc.business_logic.data_structures.grc_enum import GrcEnum
from enum import auto


class Address:
    def __new__(cls, *args, **kwargs):
        new_instance = super().__new__(cls)
        new_instance.__init__()
        return new_instance

    def __init__(self):
        self.sub_building_name: Optional[str] = None
        self.building_number: Optional[str] = None
        self.street_name: Optional[str] = None
        self.address_locality: Optional[str] = None
        self.postal_code: Optional[str] = None
        self.address_country: Optional[str] = None


class DrivingPermit:
    def __new__(cls, *args, **kwargs):
        new_instance = super().__new__(cls)
        new_instance.__init__()
        return new_instance

    def __init__(self):
        self.expiry_date: Optional[str] = None
        self.issue_number: Optional[str] = None
        self.issued_by: Optional[str] = None
        self.personal_number: Optional[str] = None


class Passport:
    def __new__(cls, *args, **kwargs):
        new_instance = super().__new__(cls)
        new_instance.__init__()
        return new_instance

    def __init__(self):
        self.document_number: Optional[str] = None
        self.icao_issuer_code: Optional[str] = None
        self.expiry_date: Optional[str] = None


class ReturnCodes(GrcEnum):
    A = "There are issues with the address provided by the applicant. Either the applicant is not known to currently live at the address given, or there's a record of the applicant having changed their address, or the applicant is known to live at a more recent address than the one given."
    D = "There are issues with a piece of evidence that the applicant provided. The piece of evidence provided is potentially forged or counterfeit, or it has expired, or it is not known to exist, or it has not been found in authoritative source records."
    F = "The applicant's details may be linked to fraudulent activity. Specifically, the applicant's name and date of birth have been linked to a known fraudulent identity."
    N = "There are issues with the applicant’s personal details. The applicant’s name and date of birth do not appear to exist in authoritative source records."
    P = "The applicant might be a politically exposed person (PEP), including that they have the either the same name as a PEP or the same name and date of birth as a PEP."
    T = "There is potential fraud, specifically that there have been a lot of checks on the applicant recently."
    V = "There are problems with proving the applicant is who they say they are, including they either do not look like the person on a piece of evidence they provided or have not successfully completed knowledge based verification questions (KBVs)."
    X = "There is insufficient evidence to prove the applicant’s identity, including that either the applicant is not able to present any type of evidence that we accept or there’s not enough information about the applicant to create the required number of KBV questions."
    Z = "The applicant has been identified as someone who’s died, including that they may have the same name, date of birth and address as someone who’s died, or name and address as someone who’s died, or name and date of birth as someone who's died."


class OneLoginData:
    def __new__(cls, *args, **kwargs):
        new_instance = super().__new__(cls)
        new_instance.__init__()
        return new_instance

    def __init__(self):
        self.sub: Optional[str] = None

        self.email: Optional[str] = None
        self.phone_number: Optional[str] = None

        self.first_name: Optional[str] = None
        self.middle_names: Optional[str] = None
        self.last_name: Optional[str] = None

        self.date_of_birth: Optional[datetime.date] = None

        self.address: Optional[Address] = Address()

        self.passport: Optional[Passport] = Passport()

        self.driving_permit: Optional[DrivingPermit] = DrivingPermit()

        self.return_codes: List[ReturnCodes] = []

        self.identity_eligible: Optional[bool] = None

        self.identity_verified: Optional[bool] = None

        self.had_photo_id: Optional[bool] = False

    def set_return_codes_from_strings(self, codes: List[str]):
        self.return_codes = [{"code": code , "description": ReturnCodes[code].value} for code in codes if code in ReturnCodes.__members__]