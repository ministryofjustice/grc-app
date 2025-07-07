from flask import Blueprint, flash, render_template, request, url_for, session, g
from grc.business_logic.constants.base import BaseConstants as c
from grc.business_logic.data_store import DataStore
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.external_services.gov_uk_notify import GovUkNotify
from grc.start_application.forms import EmailAddressForm, SecurityCodeForm, OverseasCheckForm, \
    OverseasApprovedCheckForm, DeclarationForm
from grc.utils.get_next_page import get_next_page_global, get_previous_page_global
from grc.utils.decorators import LoginRequired, EmailRequired, BeforeOneLogin, UnverifiedLoginRequired
from grc.utils.reference_number import reference_number_string
from grc.utils.redirect import local_redirect
from grc.utils.logger import LogLevel, Logger
from grc.utils.strtobool import strtobool

startApplication = Blueprint('startApplication', __name__)
logger = Logger()


@startApplication.route('/email', methods=['GET', 'POST'])
@UnverifiedLoginRequired
@BeforeOneLogin
def index():
    form = EmailAddressForm()

    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        session['email'] = email
        session['lang_code'] = g.lang_code
        GovUkNotify().send_email_security_code(email)
        return local_redirect(url_for('startApplication.securityCode'))

    return render_template(
        'start-application/email-address.html',
        form=form
    )

@startApplication.route('/security-code', methods=['GET', 'POST'])
@UnverifiedLoginRequired
@EmailRequired
@BeforeOneLogin
def securityCode():
    form = SecurityCodeForm()
    email = session.get('email')

    if request.method == 'POST':
        if form.validate_on_submit():
            session['reference_number'] = session['reference_number_unverified']
            session['identity_verified'] = True
            return local_redirect(url_for('startApplication.reference'))
        logger.log(LogLevel.WARN, f"{logger.mask_email_address(email)} entered an incorrect security code")

    elif request.args.get('resend') == 'true':
        GovUkNotify().send_email_security_code(email)
        flash(c.RESEND_SECURITY_CODE, 'email')

    return render_template(
        'security-code.html',
        form=form,
        email=email
    )

@startApplication.route('/back-to-is-first-visit', methods=['GET', 'POST'])
@LoginRequired
def backToIdentityEligible():
    return local_redirect(url_for('oneLogin.identityEligibility'))

@startApplication.route('/reference-number', methods=['GET'])
@LoginRequired
def reference():
    return render_template(
        'start-application/reference-number.html',
        reference_number=reference_number_string(session['reference_number'])
    )

@startApplication.route('/overseas-check', methods=['GET', 'POST'])
@LoginRequired
def overseas_check():
    form = OverseasCheckForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if form.validate_on_submit():
        application_data.confirmation_data.gender_recognition_outside_uk = strtobool(form.overseasCheck.data)

        if not application_data.confirmation_data.gender_recognition_outside_uk:
            application_data.confirmation_data.gender_recognition_from_approved_country = None

        DataStore.save_application(application_data)

        if application_data.confirmation_data.gender_recognition_outside_uk:
            return get_next_page(application_data, 'startApplication.overseas_approved_check')
        else:
            return get_next_page(application_data, 'startApplication.declaration')

    elif request.method == 'GET':
        form.overseasCheck.data = application_data.confirmation_data.gender_recognition_outside_uk

    return render_template(
        'start-application/overseas-check.html',
        form=form,
        back=get_previous_page(application_data, 'startApplication.reference')
    )


@startApplication.route('/overseas-approved-check', methods=['GET', 'POST'])
@LoginRequired
def overseas_approved_check():
    form = OverseasApprovedCheckForm()
    application_data = DataStore.load_application_by_session_reference_number()

    if form.validate_on_submit():
        application_data.confirmation_data.gender_recognition_from_approved_country = strtobool(form.overseasApprovedCheck.data)
        DataStore.save_application(application_data)

        return get_next_page(application_data, 'startApplication.declaration')

    elif request.method == 'GET':
        form.overseasApprovedCheck.data = application_data.confirmation_data.gender_recognition_from_approved_country

    return render_template(
        'start-application/overseas-approved-check.html',
        form=form,
        countries=c.APPROVED_COUNTRIES,
        back=get_previous_page(application_data, 'startApplication.overseas_check')
    )


@startApplication.route('/declaration', methods=['GET', 'POST'])
@LoginRequired
def declaration():
    form = DeclarationForm()
    application_data = DataStore.load_application_by_session_reference_number()
    back_link = ('startApplication.overseas_approved_check'
                 if application_data.confirmation_data.gender_recognition_outside_uk
                 else 'startApplication.overseas_check')

    if request.method == 'POST':
        if form.validate_on_submit():
            application_data.confirmation_data.consent_to_GRO_contact = form.consent.data
            DataStore.save_application(application_data)

            return get_next_page(application_data, 'taskList.index')

    else:
        form.consent.data = application_data.confirmation_data.consent_to_GRO_contact

    return render_template(
        'start-application/declaration.html',
        form=form,
        back=get_previous_page(application_data, back_link)
    )

@startApplication.route('/back-from-email', methods=['GET'])
def backFromEmail():
    session.pop('reference_number_unverified')
    return local_redirect(url_for('oneLogin.referenceNumber'))

def get_next_page(application_data: ApplicationData, next_page_in_journey: str):
    return get_next_page_global(
        next_page_in_journey=next_page_in_journey,
        section_check_your_answers_page=None,
        section_status=application_data.confirmation_data.section_status,
        application_data=application_data)


def get_previous_page(application_data: ApplicationData, previous_page_in_journey: str):
    return get_previous_page_global(
        previous_page_in_journey=previous_page_in_journey,
        section_check_your_answers_page=None,
        section_status=application_data.confirmation_data.section_status,
        application_data=application_data)
