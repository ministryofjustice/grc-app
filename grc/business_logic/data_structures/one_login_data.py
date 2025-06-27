import datetime
from typing import Optional
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
    A = auto()
    D = auto()
    F = auto()
    N = auto()
    P = auto()
    T = auto()
    V = auto()
    X = auto()
    Z = auto()


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

        self.return_codes: Optional[ReturnCodes] = None

        self.identity_eligible: Optional[bool] = None

        self.identity_verified: Optional[bool] = None

        self.had_photo_id: Optional[bool] = False