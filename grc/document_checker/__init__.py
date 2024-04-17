from flask import Blueprint, flash, render_template, request, url_for
from grc.document_checker.constants import DocumentCheckerConstants as c
from grc.document_checker.doc_checker_data_store import DocCheckerDataStore
from grc.document_checker.doc_checker_state import DocCheckerState, CurrentlyInAPartnershipEnum
from grc.document_checker.forms import PreviousNamesCheck, MarriageCivilPartnershipForm, PlanToRemainInAPartnershipForm, \
    PartnerDiedForm, PreviousPartnershipEndedForm, GenderRecognitionOutsideUKForm, EmailForm
from grc.external_services.gov_uk_notify import GovUkNotify
from grc.utils.strtobool import strtobool
from grc.utils.redirect import local_redirect

documentChecker = Blueprint('documentChecker', __name__)


@documentChecker.route('/check-documents', methods=['GET', 'POST'])
def index():
    return render_template('document-checker/start.html')


@documentChecker.route('/check-documents/changed-name-to-reflect-gender', methods=['GET', 'POST'])
def previousNamesCheck():
    form = PreviousNamesCheck()
    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()

    if form.validate_on_submit():
        doc_checker_state_.changed_name_to_reflect_gender = strtobool(form.changed_name_to_reflect_gender.data)
        DocCheckerDataStore.save_doc_checker_state(doc_checker_state_)

        return local_redirect(url_for('documentChecker.currentlyInAPartnership'))

    if request.method == 'GET':
        form.changed_name_to_reflect_gender.data = doc_checker_state_.changed_name_to_reflect_gender

    return render_template(
        'document-checker/previous-names-check.html',
        form=form
    )


@documentChecker.route('/check-documents/currently-in-a-partnership', methods=['GET', 'POST'])
def currentlyInAPartnership():
    form = MarriageCivilPartnershipForm()
    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()

    if form.validate_on_submit():
        doc_checker_state_.currently_in_a_partnership = CurrentlyInAPartnershipEnum(
            form.currently_in_a_partnership.data)
        DocCheckerDataStore.save_doc_checker_state(doc_checker_state_)

        if doc_checker_state_.is_currently_in_partnership:
            next_step = 'documentChecker.planToRemainInAPartnership'
        else:
            next_step = 'documentChecker.previousPartnershipPartnerDied'

        return local_redirect(url_for(next_step))

    if request.method == 'GET':
        form.currently_in_a_partnership.data = (
            doc_checker_state_.currently_in_a_partnership.name
            if doc_checker_state_.currently_in_a_partnership is not None
            else None
        )

    return render_template(
        'document-checker/currently_in_a_partnership.html',
        form=form,
        CurrentlyInAPartnershipEnum=CurrentlyInAPartnershipEnum
    )


@documentChecker.route('/check-documents/plan-to-remain-in-a-partnership', methods=['GET', 'POST'])
def planToRemainInAPartnership():
    form = PlanToRemainInAPartnershipForm()
    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()

    if form.validate_on_submit():
        doc_checker_state_.plan_to_remain_in_a_partnership = strtobool(form.plan_to_remain_in_a_partnership.data)
        DocCheckerDataStore.save_doc_checker_state(doc_checker_state_)

        return local_redirect(url_for('documentChecker.genderRecognitionOutsideUK'))

    form.plan_to_remain_in_a_partnership.data = doc_checker_state_.plan_to_remain_in_a_partnership

    question = c.PLAN_TO_REMAIN_MARRIED if doc_checker_state_.is_married else c.PLAN_TO_REMAIN_IN_CIVIL_PARTNERSHIP

    return render_template(
        'document-checker/plan-to-remain-in-a-partnership.html',
        form=form,
        question=question
    )


@documentChecker.route('/check-documents/previous-partnership-partner-died', methods=['GET', 'POST'])
def previousPartnershipPartnerDied():
    form = PartnerDiedForm()
    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()

    if form.validate_on_submit():
        doc_checker_state_.previous_partnership_partner_died = strtobool(form.previous_partnership_partner_died.data)
        DocCheckerDataStore.save_doc_checker_state(doc_checker_state_)

        return local_redirect(url_for('documentChecker.previousPartnershipEnded'))

    if request.method == 'GET':
        form.previous_partnership_partner_died.data = doc_checker_state_.previous_partnership_partner_died

    return render_template(
        'document-checker/partner-died.html',
        form=form
    )


@documentChecker.route('/check-documents/previous-partnership-ended', methods=['GET', 'POST'])
def previousPartnershipEnded():
    form = PreviousPartnershipEndedForm()
    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()

    if form.validate_on_submit():
        doc_checker_state_.previous_partnership_ended = strtobool(form.previous_partnership_ended.data)
        DocCheckerDataStore.save_doc_checker_state(doc_checker_state_)

        return local_redirect(url_for('documentChecker.genderRecognitionOutsideUK'))

    if request.method == 'GET':
        form.previous_partnership_ended.data = doc_checker_state_.previous_partnership_ended

    return render_template(
        'document-checker/previous-partnership-ended.html',
        form=form
    )


@documentChecker.route('/check-documents/gender-recognition-outside-uk', methods=['GET', 'POST'])
def genderRecognitionOutsideUK():
    form = GenderRecognitionOutsideUKForm()
    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()

    if form.validate_on_submit():
        doc_checker_state_.gender_recognition_outside_uk = strtobool(form.gender_recognition_outside_uk.data)
        DocCheckerDataStore.save_doc_checker_state(doc_checker_state_)

        return local_redirect(url_for('documentChecker.your_documents'))

    if request.method == 'GET':
        form.gender_recognition_outside_uk.data = doc_checker_state_.gender_recognition_outside_uk

    return render_template(
        'document-checker/gender-recognition-outside-uk.html',
        form=form,
        doc_checker_state=doc_checker_state_,
        countries=c.APPROVED_COUNTRIES
    )


@documentChecker.route('/check-documents/your-documents', methods=['GET', 'POST'])
def your_documents():
    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()

    if not hasUserAnswersAllTheQuestions():
        return local_redirect(getUrlForNextUnansweredQuestion())

    return render_template(
        'document-checker/your-documents.html',
        doc_checker_state=doc_checker_state_,
        context=get_context(doc_checker_state_)
    )


@documentChecker.route('/check-documents/email-address', methods=['GET', 'POST'])
def askForEmailAddress():
    if not hasUserAnswersAllTheQuestions():
        return local_redirect(getUrlForNextUnansweredQuestion())

    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()
    form = EmailForm()

    if form.validate_on_submit():
        try:
            docs_required_dict: dict = doc_checker_state_.get_list_of_documents_required_values()
            GovUkNotify().send_email_documents_you_need_for_your_grc_application(
                email_address=form.email_address.data,
                documents_required=docs_required_dict
            )

            return local_redirect(url_for('documentChecker.emailSent'))
        except BaseException as err:
            error = err.args[0].json()
            flash(error['errors'][0]['message'], 'error')

    return render_template(
        'document-checker/email-address.html',
        form=form
    )


@documentChecker.route('/check-documents/email-sent', methods=['GET'])
def emailSent():
    return render_template('document-checker/email-sent.html')


def hasUserAnswersAllTheQuestions() -> bool:
    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()

    if doc_checker_state_.changed_name_to_reflect_gender is None: return False
    if doc_checker_state_.currently_in_a_partnership is None: return False
    if doc_checker_state_.is_currently_in_partnership and doc_checker_state_.plan_to_remain_in_a_partnership is None: return False
    if doc_checker_state_.is_not_in_partnership and doc_checker_state_.previous_partnership_partner_died is None: return False
    if doc_checker_state_.is_not_in_partnership and doc_checker_state_.previous_partnership_ended is None: return False
    if doc_checker_state_.gender_recognition_outside_uk is None: return False
    return True


def getUrlForNextUnansweredQuestion() -> str:
    doc_checker_state_ = DocCheckerDataStore.load_doc_checker_state()

    if doc_checker_state_.changed_name_to_reflect_gender is None: return url_for('documentChecker.previousNamesCheck')
    if doc_checker_state_.currently_in_a_partnership is None: return url_for('documentChecker.currentlyInAPartnership')
    if doc_checker_state_.is_currently_in_partnership and doc_checker_state_.plan_to_remain_in_a_partnership is None: return url_for(
        'documentChecker.planToRemainInAPartnership')
    if doc_checker_state_.is_not_in_partnership and doc_checker_state_.previous_partnership_partner_died is None: return url_for(
        'documentChecker.previousPartnershipPartnerDied')
    if doc_checker_state_.is_not_in_partnership and doc_checker_state_.previous_partnership_ended is None: return url_for(
        'documentChecker.previousPartnershipEnded')
    if doc_checker_state_.gender_recognition_outside_uk is None: return url_for(
        'documentChecker.genderRecognitionOutsideUK')
    return url_for('documentChecker.your_documents')


def get_context(state: DocCheckerState) -> dict:
    context = {}
    in_civil_partnership = state.is_in_civil_partnership

    if state.need_to_send_statutory_declaration_for_applicant_in_partnership and in_civil_partnership:
        context['stat_dec_applicant_summary'] = c.STAT_DEC_APPLICANTS_CIVIL_PARTNERSHIP_SUMMARY
    else:
        context['stat_dec_applicant_summary'] = c.STAT_DEC_MARRIED_APPLICANTS_SUMMARY

    if state.need_to_send_partners_statutory_declaration and in_civil_partnership:
        context['stat_dec_partner_summary'] = c.STAT_DEC_CIVIL_PARTNER_SUMMARY
        context['stat_dec_partner_p1'] = c.STAT_DEC_CIVIL_PARTNER_P1
        context['stat_dec_partner_p2'] = c.STAT_DEC_CIVIL_PARTNER_P2
        context['stat_dec_partner_p3'] = c.STAT_DEC_CIVIL_PARTNER_P3
    else:
        context['stat_dec_partner_summary'] = c.STAT_DEC_SPOUSE_SUMMARY
        context['stat_dec_partner_p1'] = c.STAT_DEC_SPOUSE_P1
        context['stat_dec_partner_p2'] = c.STAT_DEC_SPOUSE_P2
        context['stat_dec_partner_p3'] = c.STAT_DEC_SPOUSE_P3

    if state.need_to_send_partnership_certificate and in_civil_partnership:
        context['partner_cert_summary'] = c.PARTNER_CP_CERT_SUMMARY
        context['partner_cert_p1'] = c.PARTNER_CP_CERT_P1
    else:
        context['partner_cert_summary'] = c.PARTNER_MARRIAGE_CERT_SUMMARY
        context['partner_cert_p1'] = c.PARTNER_MARRIAGE_CERT_P1

    return context
