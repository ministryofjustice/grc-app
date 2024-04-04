from grc.utils.application_files import ApplicationFiles
from tests.grc.helpers.data.uploads import UploadsHelpers


class TestApplicationFilesHelpers:
    def test_get_files_for_section_medical_reports(self, test_application):
        data = test_application.application_data()
        data.uploads_data.medical_reports = UploadsHelpers.medical_reports_uploads(3, False)
        application_files = ApplicationFiles()
        test_medical_report_files = application_files.get_files_for_section('medicalReports', data)
        assert test_medical_report_files[0].aws_file_name == 'aws_medical_file_name_1'
        assert test_medical_report_files[0].original_file_name == 'original_medical_file_name_1'
        assert test_medical_report_files[0].password_required is False
        assert test_medical_report_files[1].aws_file_name == 'aws_medical_file_name_2'
        assert test_medical_report_files[1].original_file_name == 'original_medical_file_name_2'
        assert test_medical_report_files[1].password_required is False
        assert test_medical_report_files[2].aws_file_name == 'aws_medical_file_name_3'
        assert test_medical_report_files[2].original_file_name == 'original_medical_file_name_3'
        assert test_medical_report_files[2].password_required is False

    def test_get_files_for_section_evidence_of_living_in_gender_uploads(self, test_application):
        data = test_application.application_data()
        data.uploads_data.medical_reports = UploadsHelpers.evidence_of_living_in_gender_uploads(3, False)
        application_files = ApplicationFiles()
        test_ev_living_in_gender_files = application_files.get_files_for_section('medicalReports', data)
        assert test_ev_living_in_gender_files[0].aws_file_name == 'aws_ev_living_in_gender_file_name_1'
        assert test_ev_living_in_gender_files[0].original_file_name == 'original_ev_living_in_gender_file_name_1'
        assert test_ev_living_in_gender_files[0].password_required is False
        assert test_ev_living_in_gender_files[1].aws_file_name == 'aws_ev_living_in_gender_file_name_2'
        assert test_ev_living_in_gender_files[1].original_file_name == 'original_ev_living_in_gender_file_name_2'
        assert test_ev_living_in_gender_files[1].password_required is False
        assert test_ev_living_in_gender_files[2].aws_file_name == 'aws_ev_living_in_gender_file_name_3'
        assert test_ev_living_in_gender_files[2].original_file_name == 'original_ev_living_in_gender_file_name_3'
        assert test_ev_living_in_gender_files[2].password_required is False

    def test_get_files_for_section_overseas_documents_uploads_uploads(self, test_application):
        data = test_application.application_data()
        data.uploads_data.medical_reports = UploadsHelpers.overseas_documents_uploads(3, False)
        application_files = ApplicationFiles()
        test_overseas_documents_files = application_files.get_files_for_section('medicalReports', data)
        assert test_overseas_documents_files[0].aws_file_name == 'aws_overseas_doc_file_name_1'
        assert test_overseas_documents_files[0].original_file_name == 'original_overseas_doc_file_name_1'
        assert test_overseas_documents_files[0].password_required is False
        assert test_overseas_documents_files[1].aws_file_name == 'aws_overseas_doc_file_name_2'
        assert test_overseas_documents_files[1].original_file_name == 'original_overseas_doc_file_name_2'
        assert test_overseas_documents_files[1].password_required is False
        assert test_overseas_documents_files[2].aws_file_name == 'aws_overseas_doc_file_name_3'
        assert test_overseas_documents_files[2].original_file_name == 'original_overseas_doc_file_name_3'
        assert test_overseas_documents_files[2].password_required is False

    def test_get_section_name(self):
        assert ApplicationFiles().get_section_name('medicalReports') == 'Medical Reports'
        assert ApplicationFiles().get_section_name('genderEvidence') == 'Gender Evidence'
        assert ApplicationFiles().get_section_name('nameChange') == 'Name Change'
        assert ApplicationFiles().get_section_name('marriageDocuments') == 'Marriage Documents'
        assert ApplicationFiles().get_section_name('overseasCertificate') == 'Overseas Certificate'
        assert ApplicationFiles().get_section_name('statutoryDeclarations') == 'Statutory Declarations'

