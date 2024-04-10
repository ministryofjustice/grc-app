from grc.utils.application_files import ApplicationFiles
from tests.grc.helpers.data.uploads import UploadsHelpers


class TestApplicationFilesHelpers:
    def test_get_files_for_section_medical_reports(self, test_application):
        data = test_application.application_data()
        upload_helper = UploadsHelpers('medicalReports')
        non_pdfs = upload_helper.get_uploads_object_data({'jpeg': 1, 'tiff': 1})
        pdfs = upload_helper.get_uploads_object_data_pdf(2, 1)
        data.uploads_data.medical_reports = pdfs + non_pdfs
        application_files = ApplicationFiles()
        test_medical_report_files = application_files.get_files_for_section('medicalReports', data)
        assert test_medical_report_files[0].aws_file_name == 'aws_medicalreports_name_1.pdf'
        assert test_medical_report_files[0].original_file_name == 'original_medicalreports_name_1.pdf'
        assert test_medical_report_files[0].password_required is True
        assert test_medical_report_files[1].aws_file_name == 'aws_medicalreports_name_2.pdf'
        assert test_medical_report_files[1].original_file_name == 'original_medicalreports_name_2.pdf'
        assert test_medical_report_files[1].password_required is False
        assert test_medical_report_files[2].aws_file_name == 'aws_medicalreports_name_1.jpeg'
        assert test_medical_report_files[2].original_file_name == 'original_medicalreports_name_1.jpeg'
        assert test_medical_report_files[2].password_required is False
        assert test_medical_report_files[3].aws_file_name == 'aws_medicalreports_name_1.tiff'
        assert test_medical_report_files[3].original_file_name == 'original_medicalreports_name_1.tiff'
        assert test_medical_report_files[3].password_required is False

    def test_get_files_for_section_evidence_of_living_in_gender_uploads(self, test_application):
        data = test_application.application_data()
        upload_helper = UploadsHelpers('genderEvidence')
        data.uploads_data.evidence_of_living_in_gender = upload_helper.get_uploads_object_data({'jpeg': 2, 'tiff': 1})
        application_files = ApplicationFiles()
        test_ev_living_in_gender_files = application_files.get_files_for_section('genderEvidence', data)
        assert test_ev_living_in_gender_files[0].aws_file_name == 'aws_genderevidence_name_1.jpeg'
        assert test_ev_living_in_gender_files[0].original_file_name == 'original_genderevidence_name_1.jpeg'
        assert test_ev_living_in_gender_files[0].password_required is False
        assert test_ev_living_in_gender_files[1].aws_file_name == 'aws_genderevidence_name_2.jpeg'
        assert test_ev_living_in_gender_files[1].original_file_name == 'original_genderevidence_name_2.jpeg'
        assert test_ev_living_in_gender_files[1].password_required is False
        assert test_ev_living_in_gender_files[2].aws_file_name == 'aws_genderevidence_name_1.tiff'
        assert test_ev_living_in_gender_files[2].original_file_name == 'original_genderevidence_name_1.tiff'
        assert test_ev_living_in_gender_files[2].password_required is False

    def test_get_files_for_section_overseas_documents_uploads_uploads(self, test_application):
        data = test_application.application_data()
        upload_helper = UploadsHelpers('overseasCertificate')
        non_pdfs = upload_helper.get_uploads_object_data({'png': 1})
        pdfs = upload_helper.get_uploads_object_data_pdf(1)
        data.uploads_data.overseas_documents = non_pdfs + pdfs
        application_files = ApplicationFiles()
        test_overseas_certs_files = application_files.get_files_for_section('overseasCertificate', data)
        assert test_overseas_certs_files[0].aws_file_name == f'aws_overseascertificate_name_1.png'
        assert test_overseas_certs_files[0].original_file_name == 'original_overseascertificate_name_1.png'
        assert test_overseas_certs_files[0].password_required is False
        assert test_overseas_certs_files[1].aws_file_name == 'aws_overseascertificate_name_1.pdf'
        assert test_overseas_certs_files[1].original_file_name == 'original_overseascertificate_name_1.pdf'
        assert test_overseas_certs_files[1].password_required is False

    def test_get_files_for_section_name_change_documents_uploads_uploads(self, test_application):
        data = test_application.application_data()
        upload_helper = UploadsHelpers('nameChange')
        non_pdfs = upload_helper.get_uploads_object_data({'png': 1})
        pdfs = upload_helper.get_uploads_object_data_pdf(1)
        data.uploads_data.name_change_documents = non_pdfs + pdfs
        application_files = ApplicationFiles()
        test_name_change_docs = application_files.get_files_for_section('nameChange', data)
        assert test_name_change_docs[0].aws_file_name == f'aws_namechange_name_1.png'
        assert test_name_change_docs[0].original_file_name == 'original_namechange_name_1.png'
        assert test_name_change_docs[0].password_required is False
        assert test_name_change_docs[1].aws_file_name == 'aws_namechange_name_1.pdf'
        assert test_name_change_docs[1].original_file_name == 'original_namechange_name_1.pdf'
        assert test_name_change_docs[1].password_required is False

    def test_get_files_for_section_marriage_documents_uploads_uploads(self, test_application):
        data = test_application.application_data()
        upload_helper = UploadsHelpers('marriageDocuments')
        non_pdfs = upload_helper.get_uploads_object_data({'png': 1})
        pdfs = upload_helper.get_uploads_object_data_pdf(1)
        data.uploads_data.partnership_documents = non_pdfs + pdfs
        application_files = ApplicationFiles()
        test_marriage_docs_files = application_files.get_files_for_section('marriageDocuments', data)
        assert test_marriage_docs_files[0].aws_file_name == f'aws_marriagedocuments_name_1.png'
        assert test_marriage_docs_files[0].original_file_name == 'original_marriagedocuments_name_1.png'
        assert test_marriage_docs_files[0].password_required is False
        assert test_marriage_docs_files[1].aws_file_name == 'aws_marriagedocuments_name_1.pdf'
        assert test_marriage_docs_files[1].original_file_name == 'original_marriagedocuments_name_1.pdf'
        assert test_marriage_docs_files[1].password_required is False

    def test_get_files_for_section_statutory_declarations_uploads_uploads(self, test_application):
        data = test_application.application_data()
        upload_helper = UploadsHelpers('statutoryDeclarations')
        non_pdfs = upload_helper.get_uploads_object_data({'png': 1})
        pdfs = upload_helper.get_uploads_object_data_pdf(1)
        data.uploads_data.statutory_declarations = non_pdfs + pdfs
        application_files = ApplicationFiles()
        test_stat_dec_files = application_files.get_files_for_section('statutoryDeclarations', data)
        assert test_stat_dec_files[0].aws_file_name == f'aws_statutorydeclarations_name_1.png'
        assert test_stat_dec_files[0].original_file_name == 'original_statutorydeclarations_name_1.png'
        assert test_stat_dec_files[0].password_required is False
        assert test_stat_dec_files[1].aws_file_name == 'aws_statutorydeclarations_name_1.pdf'
        assert test_stat_dec_files[1].original_file_name == 'original_statutorydeclarations_name_1.pdf'
        assert test_stat_dec_files[1].password_required is False

    def test_get_section_name(self):
        assert ApplicationFiles().get_section_name('medicalReports') == 'Medical Reports'
        assert ApplicationFiles().get_section_name('genderEvidence') == 'Gender Evidence'
        assert ApplicationFiles().get_section_name('nameChange') == 'Name Change'
        assert ApplicationFiles().get_section_name('marriageDocuments') == 'Marriage Documents'
        assert ApplicationFiles().get_section_name('overseasCertificate') == 'Overseas Certificate'
        assert ApplicationFiles().get_section_name('statutoryDeclarations') == 'Statutory Declarations'

