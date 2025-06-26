from flask import Blueprint, render_template, request, redirect, session, url_for, Response, g, flash
from grc.one_login.one_login_logout import OneLoginLogout
from grc.utils.decorators import UnverifiedLoginRequired, LoginRequired, Unauthorized, AfterOneLogin
from grc.utils.redirect import local_redirect
from grc.one_login.one_login_config import OneLoginConfig
from grc.one_login.one_login_auth_request import OneLoginAuthorizationRequest
from grc.one_login.one_login_token_request import OneLoginTokenRequest
from grc.one_login.one_login_token_validator import OneLoginTokenValidator
from grc.one_login.one_login_user_info_request import OneLoginUserInfoRequest
from grc.utils.logger import LogLevel, Logger
from grc.one_login.forms import ReferenceCheckForm, IdentityEligibility, NewExistingApplicationForm
from grc.business_logic.data_store import DataStore
from grc.models import Application

logger = Logger()
oneLogin = Blueprint('oneLogin', __name__)

@oneLogin.route('/', methods=['GET', 'POST'])
@Unauthorized
def start():
    form = NewExistingApplicationForm()
    if session.get('reference_number'):
        session.pop('reference_number')
    if request.method == "POST" and form.validate_on_submit():
        application_choice = form.application_choice.data
        if application_choice == 'NEW_APPLICATION':
            session['one_login_auth'] = True
            return local_redirect(url_for('oneLogin.authenticate'))

        elif application_choice == 'EXISTING_APPLICATION':
            return local_redirect(url_for('oneLogin.referenceNumber'))

    return render_template('one-login/start.html', form=form)

@oneLogin.route('/your-reference-number', methods=['GET', 'POST'])
@Unauthorized
def referenceNumber():
    form = ReferenceCheckForm()
    if session.get('reference_number'):
        session.pop('reference_number')
    if request.method == "POST" and form.validate_on_submit():
        if form.has_reference.data == 'HAS_REFERENCE':
            reference = DataStore.compact_reference(form.reference.data)
            application = Application.query.filter_by(reference_number=reference).first()
            application_data = application.application_data()
            session['reference_number'] = reference

            if application_data.created_after_one_login:
                session['one_login_auth'] = True
                logger.log(LogLevel.INFO, f"Application with reference number {str(reference)} was created AFTER One Login implementation. Redirecting to One Login.")
                return redirect(url_for('oneLogin.authenticate'))
            else:
                session['one_login_auth'] = False
                logger.log(LogLevel.INFO, f"Application with reference number {str(reference)} was created BEFORE One Login implementation. Redirecting to original auth.")
                return local_redirect(url_for('startApplication.index'))

    return render_template('one-login/referenceNumber.html', form=form)

@oneLogin.route('/oneLogin/identity-eligibility', methods=['GET', 'POST'])
@AfterOneLogin
@UnverifiedLoginRequired
def identityEligibility():
    form = IdentityEligibility()
    application = DataStore.load_application_by_session_reference_number()

    if request.method == "POST" and form.validate_on_submit():
        identity_eligible = form.identity_eligible.data
        application.one_login_data.identity_eligible = identity_eligible
        DataStore.save_application(application)
        if identity_eligible == 'yes':
            session['identity_eligible'] = True
            return local_redirect(url_for('oneLogin.identify'))
        else:
            session['identity_eligible'] = False
            return local_redirect(url_for('startApplication.reference'))

    if request.method == "GET":
        form.identity_eligible.data = application.one_login_data.identity_eligible

    return render_template('one-login/identityEligibility.html', form=form)

@oneLogin.route('/onelogin/authenticate', methods=['GET'])
def authenticate():
    config = OneLoginConfig.get_instance()
    auth = OneLoginAuthorizationRequest(config)
    redirect_url = auth.build_authentication_redirect_url()
    return redirect(redirect_url)

@oneLogin.route('/onelogin/identify', methods=['GET'])
def identify():
    config = OneLoginConfig.get_instance()
    auth = OneLoginAuthorizationRequest(config)
    redirect_url = auth.build_identity_redirect_url()
    return redirect(redirect_url)

@oneLogin.route('/onelogin/logout', methods=['GET'])
def oneLoginSaveAndExit():
    config = OneLoginConfig.get_instance()
    logout_request = OneLoginLogout(config)
    id_token = session.get('id_token')

    if id_token is None:
        logger.log(LogLevel.WARN, "ID token not found; redirecting to start")
        return local_redirect(url_for('saveAndReturn.exitApplication'))

    try:
        redirect_url = logout_request.logout_redirect_url_to_save_page(id_token=id_token)
        return local_redirect(redirect_url)

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return local_redirect(url_for('saveAndReturn.exitApplication'))

@oneLogin.route('/one-login/back-channel-logout', methods=['POST'])
def backChannelLogout():
    logger.log(LogLevel.INFO, f'Back channel logout request received.')

    try:
        config = OneLoginConfig.get_instance()
        token_validator = OneLoginTokenValidator(config=config)
        logout_request = OneLoginLogout(config=config)
        token = request.form.get('logout_token')

        if not token:
            logger.log(LogLevel.WARN, "Logout token does not exist")
            return local_redirect(url_for('oneLogin.start'))

        token_claims = token_validator.validate_logout_token(logout_token=token)
        logout_request.end_user_session_with_sub(token_claims.get('sub', ''))

        return Response(status=200)

    except Exception as e:
        logger.log(LogLevel.ERROR, f'Received back channel request but failed to execute logout due to {str(e)}')
        return Response(status=200)

@oneLogin.route('/auth/callback', methods=['GET'])
def callbackAuthentication():
    try:
        if "error" in request.args:
            logger.log(LogLevel.ERROR, f"{request.args['error']} - {request.args.get('error_description', '')}")
            return local_redirect(url_for("oneLogin.start"))

        code = request.args.get("code")
        if not code:
            logger.log(LogLevel.ERROR, "No code received in callback.")
            return local_redirect(url_for("oneLogin.start"))

        config = OneLoginConfig.get_instance()
        token_request = OneLoginTokenRequest(config)
        token_validator = OneLoginTokenValidator(config)
        user_info_request = OneLoginUserInfoRequest(config)

        access_token, id_token = token_request.fetch_tokens_auth_request(code)
        token_validator.validate_access_id_tokens(access_token=access_token, id_token=id_token)
        session['id_token'] = id_token
        user_info = user_info_request.request_user_info(access_token)

        sub = user_info.get('sub')
        email = user_info.get('email')
        phone_number = user_info.get('phone_number')

        if session.get('reference_number'):
            application_data = DataStore.load_application_by_session_reference_number()
            if email != application_data.email_address:
                flash("The email address does not match our records for the reference number you provided.", "error")
                logout_request = OneLoginLogout(OneLoginConfig.get_instance())
                redirect_url = logout_request.logout_redirect_url_to_reference_check_page(id_token)
                session.pop('reference_number')
                logger.log(LogLevel.ERROR, "Email address does not match our records for the reference number you provided.")
                return local_redirect(redirect_url)
        else:
            application_data = DataStore.create_new_application(email_address=email)
            session['reference_number'] = application_data.reference_number
            DataStore.increment_application_sessions(application_data.reference_number)

        application_data.one_login_data.sub = sub
        application_data.one_login_data.email = email
        application_data.one_login_data.phone_number = phone_number
        DataStore.save_application(application_data)

        user_info_request.store_user_info_redis_mapping(sub)

        return local_redirect(url_for("oneLogin.identityEligibility"))

    except Exception as e:
        logger.log(LogLevel.ERROR, f"Auth callback failed: {str(e)}")
        return local_redirect(url_for("oneLogin.start"))

@oneLogin.route('/identity/callback', methods=['GET'])
def callbackIdentity():
    try:
        if "error" in request.args:
            logger.log(LogLevel.ERROR, f"{request.args['error']} - {request.args.get('error_description', '')}")
            return local_redirect(url_for("oneLogin.start"))

        code = request.args.get("code")
        if not code:
            logger.log(LogLevel.ERROR, "No code received in callback.")
            return local_redirect(url_for("oneLogin.start"))

        config = OneLoginConfig.get_instance()
        token_request = OneLoginTokenRequest(config)
        token_validator = OneLoginTokenValidator(config)
        user_info_request = OneLoginUserInfoRequest(config)

        access_token, id_token = token_request.fetch_tokens_identity_request(code)
        token_validator.validate_access_id_tokens(access_token=access_token, id_token=id_token)
        user_info = user_info_request.request_user_info(access_token)

        application_data = DataStore.load_application_by_session_reference_number()

        return_codes = user_info.get("https://vocab.account.gov.uk/v1/returnCode")
        if return_codes:
            session['identity_eligible'] = False
            session['identity_verified'] = False
            application_data.one_login_data.identity_verified = False

        else:
            session['identity_verified'] = True
            application_data.one_login_data.identity_verified = True

            addresses = user_info.get("https://vocab.account.gov.uk/v1/address")
            if addresses:
                address = addresses[0]

                building_number = address.get('buildingNumber')
                street_name = address.get('streetName')
                address_locality = address.get('addressLocality')
                postal_code = address.get('postalCode')

                application_data.one_login_data.address.sub_building_name = address.get('subBuildingName')
                application_data.one_login_data.address.building_number = building_number
                application_data.one_login_data.address.street_name = street_name
                application_data.one_login_data.address.address_locality = address_locality
                application_data.one_login_data.address.postal_code = postal_code
                application_data.one_login_data.address.address_country = address.get('addressCountry')

                if application_data.personal_details_data.address_line_one is None:
                    application_data.personal_details_data.address_line_one = f"{building_number} {street_name}".strip()

                if application_data.personal_details_data.address_town_city is None:
                    application_data.personal_details_data.address_town_city = address_locality

                if application_data.personal_details_data.address_postcode is None:
                    application_data.personal_details_data.address_postcode = postal_code

            driving_permits = user_info.get("https://vocab.account.gov.uk/v1/drivingPermit")
            if driving_permits:
                driving_permit = driving_permits[0]
                application_data.one_login_data.driving_permit.expiry_date = driving_permit.get('expiryDate')
                application_data.one_login_data.driving_permit.issue_number = driving_permit.get('issueNumber')
                application_data.one_login_data.driving_permit.issued_by = driving_permit.get('issuedBy')
                application_data.one_login_data.driving_permit.personal_number = driving_permit.get('personalNumber')
                application_data.one_login_data.has_photo_id = True

            passports = user_info.get("https://vocab.account.gov.uk/v1/passport")
            if passports:
                passport = passports[0]
                application_data.one_login_data.passport.document_number = passport.get('documentNumber')
                application_data.one_login_data.passport.icao_issuer_code = passport.get('icaoIssuerCode')
                application_data.one_login_data.passport.expiry_date = passport.get('expiryDate')
                application_data.one_login_data.has_photo_id = True

            context_jwt = user_info.get("https://vocab.account.gov.uk/v1/coreIdentityJWT")
            if context_jwt:
                name, dob = user_info_request.get_names_dob_from_context_jwt(context_jwt)
                first_name = name.get('first_name')
                middle_name = name.get('middle_names')
                last_name = name.get('last_name')

                application_data.one_login_data.first_name = first_name
                application_data.one_login_data.middle_names = middle_name
                application_data.one_login_data.last_name = last_name
                application_data.one_login_data.date_of_birth = dob

                if application_data.birth_registration_data.date_of_birth is None:
                    application_data.birth_registration_data.date_of_birth = dob

                if application_data.personal_details_data.first_name is None:
                    application_data.personal_details_data.first_name = first_name

                if application_data.personal_details_data.middle_names is None:
                    application_data.personal_details_data.middle_names = middle_name

                if application_data.personal_details_data.last_name is None:
                    application_data.personal_details_data.last_name = last_name


        if application_data.personal_details_data.contact_email_address is None:
            application_data.personal_details_data.contact_email_address = application_data.one_login_data.email

        if application_data.personal_details_data.contact_phone_number is None:
            application_data.personal_details_data.contact_phone_number = application_data.one_login_data.phone_number

        DataStore.save_application(application_data)

        return local_redirect(url_for("startApplication.reference"))

    except Exception as e:
        logger.log(LogLevel.ERROR, f"Identity callback failed: {str(e)}")
        return local_redirect(url_for("oneLogin.identityEligibility"))

@oneLogin.route('/back-from-identity', methods=['GET'])
def backFromIdentity():
    reference_number = session.get("reference_number")
    if reference_number is None:
        return local_redirect(url_for('oneLogin.start'))
    session.pop('reference_number')
    logout_request = OneLoginLogout(OneLoginConfig.get_instance())
    redirect_url = logout_request.logout_redirect_url_to_start_page(session.get('id_token'))
    return local_redirect(redirect_url)

@oneLogin.route('/back-from-reference', methods=['GET'])
def backFromReference():
    one_login_auth = session.get('one_login_auth')
    if one_login_auth is True:
        return local_redirect(url_for('oneLogin.identityEligibility'))
    else:
        session.clear()
        return local_redirect(url_for('oneLogin.referenceNumber'))

def handle_onelogin_response(code: str, fetch_tokens_func, store_user_info_func):
    config = OneLoginConfig.get_instance()
    token_request = OneLoginTokenRequest(config)
    token_validator = OneLoginTokenValidator(config)
    user_info_request = OneLoginUserInfoRequest(config)

    access_token, id_token = fetch_tokens_func(token_request, code)
    token_validator.validate_access_id_tokens(access_token=access_token, id_token=id_token)
    store_user_info_func(user_info_request, access_token, id_token)
