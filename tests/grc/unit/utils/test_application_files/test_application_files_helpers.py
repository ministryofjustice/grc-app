from grc.business_logic.data_structures.uploads_data import EvidenceFile
from grc.utils.application_files import ApplicationFiles


class TestApplicationFilesHelpers:
    def test_get_files_for_section(self, test_application):
        data = test_application.application_data()
        evidence_file = EvidenceFile()
        evidence_file.aws_file_name = 'test_aws_file_name'
        evidence_file.original_file_name = 'original_file_name'
        evidence_file.password_required = False
        data.uploads_data.medical_reports = [evidence_file, evidence_file, evidence_file]
        application_files = ApplicationFiles()
        # application_files.get_files_for_section()
        pass
