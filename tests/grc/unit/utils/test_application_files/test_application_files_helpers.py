from grc.utils.application_files import ApplicationFiles
from tests.grc.helpers.data.uploads import UploadsHelpers


class TestApplicationFilesHelpers:
    def test_get_files_for_section_medical_reports(self, test_application):
        data = test_application.application_data()
        upload_helper = UploadsHelpers('medical_reports')
        non_pdfs = upload_helper.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
        pdfs = upload_helper.get_uploads_object_data_pdf(2, 1)
        data.uploads_data.medical_reports = pdfs + non_pdfs
        application_files = ApplicationFiles()
        test_medical_report_files = application_files.get_files_for_section('medicalReports', data)
        assert test_medical_report_files[0].aws_file_name == 'aws_medical_reports_name_1.pdf'
        assert test_medical_report_files[0].original_file_name == 'original_medical_reports_name_1.pdf'
        assert test_medical_report_files[0].password_required is True
        assert test_medical_report_files[1].aws_file_name == 'aws_medical_reports_name_2.pdf'
        assert test_medical_report_files[1].original_file_name == 'original_medical_reports_name_2.pdf'
        assert test_medical_report_files[1].password_required is False
        assert test_medical_report_files[2].aws_file_name == 'aws_medical_reports_name_1_original.jpeg'
        assert test_medical_report_files[2].original_file_name == 'original_medical_reports_name_1.jpeg'
        assert test_medical_report_files[2].password_required is False
        assert test_medical_report_files[3].aws_file_name == 'aws_medical_reports_name_1_original.tiff'
        assert test_medical_report_files[3].original_file_name == 'original_medical_reports_name_1.tiff'
        assert test_medical_report_files[3].password_required is False

    def test_get_files_for_section_evidence_of_living_in_gender_uploads(self, test_application):
        data = test_application.application_data()
        upload_helper = UploadsHelpers('gender_evidence')
        data.uploads_data.evidence_of_living_in_gender = upload_helper.get_uploads_object_data({'jpeg': 2, 'tiff': 1})
        application_files = ApplicationFiles()
        test_ev_living_in_gender_files = application_files.get_files_for_section('genderEvidence', data)
        assert test_ev_living_in_gender_files[0].aws_file_name == 'aws_gender_evidence_name_1_original.jpeg'
        assert test_ev_living_in_gender_files[0].original_file_name == 'original_gender_evidence_name_1.jpeg'
        assert test_ev_living_in_gender_files[0].password_required is False
        assert test_ev_living_in_gender_files[1].aws_file_name == 'aws_gender_evidence_name_2_original.jpeg'
        assert test_ev_living_in_gender_files[1].original_file_name == 'original_gender_evidence_name_2.jpeg'
        assert test_ev_living_in_gender_files[1].password_required is False
        assert test_ev_living_in_gender_files[2].aws_file_name == 'aws_gender_evidence_name_1_original.tiff'
        assert test_ev_living_in_gender_files[2].original_file_name == 'original_gender_evidence_name_1.tiff'
        assert test_ev_living_in_gender_files[2].password_required is False

    def test_get_files_for_section_overseas_documents_uploads_uploads(self, test_application):
        data = test_application.application_data()
        upload_helper = UploadsHelpers('overseas_documents')
        non_pdfs = upload_helper.get_uploads_object_data({'png': 1})
        pdfs = upload_helper.get_uploads_object_data_pdf(1)
        data.uploads_data.overseas_documents = non_pdfs + pdfs
        application_files = ApplicationFiles()
        test_overseas_certs_files = application_files.get_files_for_section('overseasCertificate', data)
        assert test_overseas_certs_files[0].aws_file_name == f'aws_overseas_documents_name_1_original.png'
        assert test_overseas_certs_files[0].original_file_name == 'original_overseas_documents_name_1.png'
        assert test_overseas_certs_files[0].password_required is False
        assert test_overseas_certs_files[1].aws_file_name == 'aws_overseas_documents_name_1.pdf'
        assert test_overseas_certs_files[1].original_file_name == 'original_overseas_documents_name_1.pdf'
        assert test_overseas_certs_files[1].password_required is False

    def test_get_section_name(self):
        assert ApplicationFiles().get_section_name('medicalReports') == 'Medical Reports'
        assert ApplicationFiles().get_section_name('genderEvidence') == 'Gender Evidence'
        assert ApplicationFiles().get_section_name('nameChange') == 'Name Change'
        assert ApplicationFiles().get_section_name('marriageDocuments') == 'Marriage Documents'
        assert ApplicationFiles().get_section_name('overseasCertificate') == 'Overseas Certificate'
        assert ApplicationFiles().get_section_name('statutoryDeclarations') == 'Statutory Declarations'

