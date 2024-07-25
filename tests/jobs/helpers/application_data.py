from grc.business_logic.data_store import DataStore


class ApplicationDataHelpers:

    @staticmethod
    def create_new_application(email_address):
        return DataStore.create_new_application(email_address)

    @staticmethod
    def load_test_data(reference_number):
        return DataStore.load_application(reference_number)

    @staticmethod
    def save_test_data(data):
        DataStore.save_application(data)
