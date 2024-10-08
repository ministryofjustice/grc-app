from flask import Blueprint, render_template, request, url_for
from grc.business_logic.data_store import DataStore
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.business_logic.data_structures.partnership_details_data import CurrentlyInAPartnershipEnum
from grc.list_status import ListStatus
from grc.business_logic.constants.partnership_details import PartnershipDetailsConstants as c
from grc.partnership_details.forms import MarriageCivilPartnershipForm, StayTogetherForm, PartnerAgreesForm, \
    PartnerDiedForm, PreviousPartnershipEndedForm, InterimCheckForm, CheckYourAnswers, PartnerDetailsForm
from grc.utils.decorators import LoginRequired
from grc.utils.get_next_page import get_next_page_global, get_previous_page_global
from grc.utils.link_builder import LinkBuilder
from grc.utils.redirect import local_redirect
from grc.utils.strtobool import strtobool

partnershipDetails = Blueprint('partnershipDetails', __name__)


@partnershipDetails.route('/partnership-details', methods=['GET', 'POST'])
@LoginRequired
def index():
    form = MarriageCivilPartnershipForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if form.validate_on_submit():
        application_data.partnership_details_data.currently_in_a_partnership = \
            CurrentlyInAPartnershipEnum[form.currently_married.data]

        if application_data.partnership_details_data.is_currently_in_partnership:
            application_data.partnership_details_data.previous_partnership_partner_died = None
            application_data.partnership_details_data.previous_partnership_ended = None
        else:
            application_data.partnership_details_data.plan_to_remain_in_a_partnership = None
            application_data.partnership_details_data.partner_agrees = None
            application_data.partnership_details_data.confirm_understood_interim_certificate = None
            application_data.partnership_details_data.partner_title = None
            application_data.partnership_details_data.partner_first_name = None
            application_data.partnership_details_data.partner_last_name = None
            application_data.partnership_details_data.partner_postal_address = None

        DataStore.save_application(application_data)

        if application_data.partnership_details_data.currently_in_a_partnership == CurrentlyInAPartnershipEnum.NEITHER:
            return get_next_page(application_data, 'partnershipDetails.partnerDied')
        else:
            return get_next_page(application_data, 'partnershipDetails.stayTogether')

    if request.method == 'GET':
        form.currently_married.data = (
            application_data.partnership_details_data.currently_in_a_partnership.name
            if application_data.partnership_details_data.currently_in_a_partnership is not None else None)

    return render_template(
        'partnership-details/current-check.html',
        form=form,
        back=get_previous_page(application_data, 'taskList.index')
    )


@partnershipDetails.route('/partnership-details/stay-together', methods=['GET', 'POST'])
@LoginRequired
def stayTogether():
    form = StayTogetherForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if form.validate_on_submit():
        previous_value = application_data.partnership_details_data.plan_to_remain_in_a_partnership
        application_data.partnership_details_data.plan_to_remain_in_a_partnership = strtobool(form.stay_together.data)

        if not application_data.partnership_details_data.plan_to_remain_in_a_partnership:
            application_data.partnership_details_data.partner_agrees = None
            application_data.partnership_details_data.partner_title = None
            application_data.partnership_details_data.partner_first_name = None
            application_data.partnership_details_data.partner_last_name = None
            application_data.partnership_details_data.partner_postal_address = None

        if application_data.partnership_details_data.plan_to_remain_in_a_partnership == False and previous_value != False:
            # If the user has NEWLY answered 'No', then force them to re-confirm they will receive an Interim GRC
            #   Note: this mainly applies in the Change Your Answers journey
            application_data.partnership_details_data.confirm_understood_interim_certificate = None

        DataStore.save_application(application_data)

        if application_data.partnership_details_data.plan_to_remain_in_a_partnership:
            return get_next_page(application_data, 'partnershipDetails.partnerAgrees')
        else:
            return get_next_page(application_data, 'partnershipDetails.interimCheck')

    if request.method == 'GET':
        form.stay_together.data = application_data.partnership_details_data.plan_to_remain_in_a_partnership

    context = {}
    if application_data.partnership_details_data.is_married:
        context['question'] = c.PLAN_TO_REMAIN_MARRIED
    else:
        link = LinkBuilder(
            '<a href="https://www.gov.uk/convert-civil-partnership" target="_blank" class="govuk-link">',
            c.STAY_TOGETHER_HINT_TEXT_LINK,
            c.STAY_TOGETHER_HINT_TEXT_BEFORE_LINK,
            c.STAY_TOGETHER_HINT_TEXT_AFTER_LINK,
        )
        context['question'] = c.PLAN_TO_REMAIN_IN_CIVIL_PARTNERSHIP
        context['link'] = link.get_link_with_text_safe()

    return render_template(
        'partnership-details/stay-together.html',
        form=form,
        context=context,
        application_data=application_data,
        back=get_previous_page(application_data, 'partnershipDetails.index')
    )


@partnershipDetails.route('/partnership-details/partner-agrees', methods=['GET', 'POST'])
@LoginRequired
def partnerAgrees():
    form = PartnerAgreesForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if form.validate_on_submit():
        previous_value = application_data.partnership_details_data.partner_agrees
        application_data.partnership_details_data.partner_agrees = strtobool(form.partner_agrees.data)

        if application_data.partnership_details_data.partner_agrees:
            application_data.partnership_details_data.confirm_understood_interim_certificate = None
        else:
            application_data.partnership_details_data.partner_title = None
            application_data.partnership_details_data.partner_first_name = None
            application_data.partnership_details_data.partner_last_name = None
            application_data.partnership_details_data.partner_postal_address = None

        if application_data.partnership_details_data.partner_agrees == False and previous_value != False:
            # If the user has NEWLY answered 'No', then force them to re-confirm they will receive an Interim GRC
            #   Note: this mainly applies in the Change Your Answers journey
            application_data.partnership_details_data.confirm_understood_interim_certificate = None

        DataStore.save_application(application_data)

        if application_data.partnership_details_data.partner_agrees:
            return get_next_page(application_data, 'partnershipDetails.partnerDetails')
        else:
            return get_next_page(application_data, 'partnershipDetails.interimCheck')

    if request.method == 'GET':
        form.partner_agrees.data = application_data.partnership_details_data.partner_agrees

    return render_template(
        'partnership-details/partner-agrees.html',
        form=form,
        context=get_context_partner_agrees(application_data.partnership_details_data),
        application_data=application_data,
        back=get_previous_page(application_data, 'partnershipDetails.stayTogether')
    )


@partnershipDetails.route('/partnership-details/partner-details', methods=['GET', 'POST'])
@LoginRequired
def partnerDetails():
    form = PartnerDetailsForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if form.validate_on_submit():
        application_data.partnership_details_data.partner_title = form.partner_title.data
        application_data.partnership_details_data.partner_first_name = form.partner_first_name.data
        application_data.partnership_details_data.partner_last_name = form.partner_last_name.data
        application_data.partnership_details_data.partner_postal_address = form.partner_postal_address.data

        DataStore.save_application(application_data)

        return get_next_page(application_data, 'partnershipDetails.checkYourAnswers')

    if request.method == 'GET':
        form.partner_title.data = application_data.partnership_details_data.partner_title
        form.partner_first_name.data = application_data.partnership_details_data.partner_first_name
        form.partner_last_name.data = application_data.partnership_details_data.partner_last_name
        form.partner_postal_address.data = application_data.partnership_details_data.partner_postal_address

    return render_template(
        'partnership-details/partner-details.html',
        form=form,
        context=get_context_partner_details(application_data.partnership_details_data),
        application_data=application_data,
        back=get_previous_page(application_data, 'partnershipDetails.partnerAgrees')
    )


@partnershipDetails.route('/partnership-details/interim-check', methods=['GET', 'POST'])
@LoginRequired
def interimCheck():
    form = InterimCheckForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if request.method == 'POST':
        application_data.partnership_details_data.confirm_understood_interim_certificate = True
        DataStore.save_application(application_data)

        return get_next_page(application_data, 'partnershipDetails.checkYourAnswers')

    if application_data.partnership_details_data.plan_to_remain_in_a_partnership:
        back_link = 'partnershipDetails.partnerAgrees'
    else:
        back_link = 'partnershipDetails.stayTogether'

    return render_template(
        'partnership-details/interim-check.html',
        form=form,
        context=get_context_interim_check(application_data.partnership_details_data),
        back=get_previous_page(application_data, back_link),
        application_data=application_data
    )


@partnershipDetails.route('/partnership-details/partner-died', methods=['GET', 'POST'])
@LoginRequired
def partnerDied():
    form = PartnerDiedForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if form.validate_on_submit():
        application_data.partnership_details_data.previous_partnership_partner_died = strtobool(form.partner_died.data)
        DataStore.save_application(application_data)

        return get_next_page(application_data, 'partnershipDetails.endedCheck')

    if request.method == 'GET':
        form.partner_died.data = application_data.partnership_details_data.previous_partnership_partner_died

    return render_template(
        'partnership-details/partner-died.html',
        form=form,
        back=get_previous_page(application_data, 'partnershipDetails.index')
    )


@partnershipDetails.route('/partnership-details/ended-check', methods=['GET', 'POST'])
@LoginRequired
def endedCheck():
    form = PreviousPartnershipEndedForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if form.validate_on_submit():
        application_data.partnership_details_data.previous_partnership_ended = strtobool(form.previous_partnership_ended.data)
        DataStore.save_application(application_data)

        return get_next_page(application_data, 'partnershipDetails.checkYourAnswers')

    if request.method == 'GET':
        form.previous_partnership_ended.data = application_data.partnership_details_data.previous_partnership_ended

    return render_template(
        'partnership-details/ended-check.html',
        form=form,
        back=get_previous_page(application_data, 'partnershipDetails.partnerDied')
    )


@partnershipDetails.route('/partnership-details/check-your-answers', methods=['GET', 'POST'])
@LoginRequired
def checkYourAnswers():
    form = CheckYourAnswers()
    application_data = DataStore.load_application_by_session_reference_number()

    if application_data.partnership_details_data.section_status != ListStatus.COMPLETED:
        return local_redirect(url_for('taskList.index'))

    if request.method == 'POST':
        return local_redirect(url_for('taskList.index'))

    if application_data.partnership_details_data.is_not_in_partnership:
        back_link = 'partnershipDetails.endedCheck'
    elif application_data.partnership_details_data.is_interim_certificate:
        back_link = 'partnershipDetails.interimCheck'
    else:
        back_link = 'partnershipDetails.partnerDetails'

    return render_template(
        'partnership-details/check-your-answers.html',
        form=form,
        content=get_context_check_your_answers(application_data.partnership_details_data),
        application_data=application_data,
        back=get_previous_page(application_data, back_link)
    )


def get_next_page(application_data: ApplicationData, next_page_in_journey: str):
    return get_next_page_global(
        next_page_in_journey=next_page_in_journey,
        section_check_your_answers_page='partnershipDetails.checkYourAnswers',
        section_status=application_data.partnership_details_data.section_status,
        application_data=application_data)


def get_previous_page(application_data: ApplicationData, previous_page_in_journey: str):
    return get_previous_page_global(
        previous_page_in_journey=previous_page_in_journey,
        section_check_your_answers_page='partnershipDetails.checkYourAnswers',
        section_status=application_data.partnership_details_data.section_status,
        application_data=application_data)


def get_context_partner_agrees(partnership_data) -> dict:
    context = {}
    anchor = ('<a href="https://www.gov.uk/government/publications/gender-recognition-certificate-statutory-'
              'declarations-for-applicants" rel="noreferrer noopener" target="_blank" class="govuk-link">')
    if partnership_data.is_in_civil_partnership:
        link = LinkBuilder(
            anchor,
            c.PARTNER_AGREES_CP_LINK_TEXT,
            c.PARTNER_AGREES_CP_TEXT_BEFORE_LINK,
            c.PARTNER_AGREES_TEXT_AFTER_LINK,
        )
        context['question'] = c.PARTNER_AGREES_CP_QUESTION
        context['link'] = link.get_link_with_text_safe()
    else:
        link = LinkBuilder(
            anchor,
            c.PARTNER_AGREES_MARRIED_LINK_TEXT,
            c.PARTNER_AGREES_MARRIED_TEXT_BEFORE_LINK,
            c.PARTNER_AGREES_TEXT_AFTER_LINK
        )
        context['question'] = c.PARTNER_AGREES_MARRIED_QUESTION
        context['link'] = link.get_link_with_text_safe()

    return context


def get_context_partner_details(partnership_data) -> dict:
    context = {}
    if partnership_data.is_in_civil_partnership:
        context['header'] = c.PARTNER_DETAILS_CP_HEADER
        context['p'] = c.PARTNER_DETAILS_CP_PARAGRAPH + c.PARTNER_DETAILS_PARAGRAPH_2
    else:
        context['header'] = c.PARTNER_DETAILS_MARRIED_HEADER
        context['p'] = c.PARTNER_DETAILS_MARRIED_PARAGRAPH + c.PARTNER_DETAILS_PARAGRAPH_2

    return context


def get_context_check_your_answers(partnership_data) -> dict:
    context = {}
    if partnership_data.is_in_civil_partnership:
        context['partner_agrees_title'] = c.PARTNER_DETAILS_CYA_PARTNER_CP_AGREES
        context['stay_together_title'] = c.PARTNER_DETAILS_CYA_STAY_TOGETHER_CP
        context['partner_name'] = "civil partner"
        context['in_your_partnership_name'] = "in your civil partnership"
        context['partner_name_cap'] = c.PARTNER_DETAILS_CYA_PARTNER_CP_CAPITALISED
        context['partner_name_post_code'] = c.PARTNER_DETAILS_CYA_PARTNER_CP_CAPITALISED_ADDRESS
    else:
        context['partner_agrees_title'] = c.PARTNER_DETAILS_CYA_PARTNER_MARRIED_AGREES
        context['stay_together_title'] = c.PARTNER_DETAILS_CYA_STAY_TOGETHER_MARRIED
        context['partner_name'] = "spouse"
        context['in_your_partnership_name'] = "married"
        context['partner_name_cap'] = c.PARTNER_DETAILS_CYA_PARTNER_MARRIED_CAPITALISED
        context['partner_name_post_code'] = c.PARTNER_DETAILS_CYA_PARTNER_MARRIED_CAPITALISED_ADDRESS

    return context


def get_context_interim_check(partnership_data) -> dict:
    context = {}
    if partnership_data.is_in_civil_partnership:
        context['interim_p1'] = c.INTERIM_P1_CP
        context['interim_p2'] = c.INTERIM_P2_CP
        context['interim_p3'] = c.INTERIM_P3_CP
        context['interim_p5'] = c.INTERIM_P5_CP
    else:
        context['interim_p1'] = c.INTERIM_P1_MARRIED
        context['interim_p2'] = c.INTERIM_P2_MARRIED
        context['interim_p3'] = c.INTERIM_P3_MARRIED
        context['interim_p5'] = c.INTERIM_P5_MARRIED

    context['interim_p4'] = c.INTERIM_P4

    return context
