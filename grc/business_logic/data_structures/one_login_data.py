import datetime
from typing import Optional, List
from grc.business_logic.data_structures.grc_enum import GrcEnum
from enum import auto


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

