from datetime import datetime

class ApplicationData:

    def __init__(self):
        self.reference_number: str = "123"
        self.email_address: str = "mgb"
        self.updated: datetime = "2024-06-28 14:30:00"

    def get_data(self):
        # Method to retrieve both date and number variables
        return {
            "reference_number": self.reference_number,
            "email_address": self.email_address,
            "updated": self.updated
        }