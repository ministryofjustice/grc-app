from grc.business_logic.data_structures.uploads_data import EvidenceFile


class UploadsHelpers:

    @staticmethod
    def medical_reports_uploads(number_of_files, is_password_required):
        files = []
        for i in range(1, number_of_files + 1):
            ef = EvidenceFile()
            ef.aws_file_name = f'aws_medical_file_name_{i}'
            ef.original_file_name = f'original_medical_file_name_{i}'
            ef.password_required = is_password_required
            files.append(ef)
        return files

    @staticmethod
    def evidence_of_living_in_gender_uploads(number_of_files, is_password_required):
        files = []
        for i in range(1, number_of_files + 1):
            ef = EvidenceFile()
            ef.aws_file_name = f'aws_ev_living_in_gender_file_name_{i}'
            ef.original_file_name = f'original_ev_living_in_gender_file_name_{i}'
            ef.password_required = is_password_required
            files.append(ef)
        return files

    @staticmethod
    def name_change_documents_uploads(number_of_files, is_password_required):
        files = []
        for i in range(1, number_of_files + 1):
            ef = EvidenceFile()
            ef.aws_file_name = f'aws_name_change_doc_file_name_{i}'
            ef.original_file_name = f'original_name_change_doc_file_name_{i}'
            ef.password_required = is_password_required
            files.append(ef)
        return files

    @staticmethod
    def partnership_documents_uploads(number_of_files, is_password_required):
        files = []
        for i in range(1, number_of_files + 1):
            ef = EvidenceFile()
            ef.aws_file_name = f'aws_partnership_doc_file_name_{i}'
            ef.original_file_name = f'original_partnership_doc_file_name_{i}'
            ef.password_required = is_password_required
            files.append(ef)
        return files

    @staticmethod
    def overseas_documents_uploads(number_of_files, is_password_required):
        files = []
        for i in range(1, number_of_files + 1):
            ef = EvidenceFile()
            ef.aws_file_name = f'aws_overseas_doc_file_name_{i}'
            ef.original_file_name = f'original_overseas_doc_file_name_{i}'
            ef.password_required = is_password_required
            files.append(ef)
        return files

    @staticmethod
    def statutory_declarations_uploads(number_of_files, is_password_required):
        files = []
        for i in range(1, number_of_files + 1):
            ef = EvidenceFile()
            ef.aws_file_name = f'aws_stat_dec_file_name_{i}'
            ef.original_file_name = f'original_stat_dec_doc_file_name_{i}'
            ef.password_required = is_password_required
            files.append(ef)
        return files
