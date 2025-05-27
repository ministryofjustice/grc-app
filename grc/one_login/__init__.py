from flask import Blueprint, render_template, request, redirect, session, url_for, Response, g
from grc.one_login.one_login_logout import OneLoginLogout
from grc.utils.decorators import LoginRequired, Unauthorized
from grc.utils.redirect import local_redirect
from grc.one_login.one_login_config import get_onelogin_config
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

    if request.method == "POST" and form.validate_on_submit():
        application_choice = form.application_choice.data
        if application_choice == 'NEW_APPLICATION':
            return local_redirect(url_for('oneLogin.authenticate'))

        elif application_choice == 'EXISTING_APPLICATION':
            return local_redirect(url_for('oneLogin.reference_number'))

    return render_template('one-login/start.html', form=form)

@oneLogin.route('/your-reference-number', methods=['GET', 'POST'])
def reference_number():
    form = ReferenceCheckForm()

    if request.method == "POST" and form.validate_on_submit():
        if form.reference.data == 'HAS_REFERENCE':
            reference = DataStore.compact_reference(form.reference.data)
            application = Application.query.filter_by(reference_number=reference).first()

            if application is None:
                form.reference.errors.append('Enter a valid reference number')
                return render_template('one-login/start.html', form=form)

            application_data = application.application_data()
            session['reference_number'] = reference

            if not application_data.created_after_one_login:
                logger.log(LogLevel.INFO, f"Application with reference number {str(reference)} was created BEFORE One Login implementation. Redirecting to original auth.")
                return local_redirect(url_for('startApplication.index'))

            logger.log(LogLevel.INFO, f"Application with reference number {str(reference)} was created AFTER One Login implementation. Redirecting to One Login.")
            return redirect(url_for('oneLogin.authenticate'))

    return render_template('one-login/referenceNumber.html', form=form)

@oneLogin.route('/oneLogin/identity-eligibility', methods=['GET', 'POST'])
@LoginRequired
def identityEligibility():
    form = IdentityEligibility()
    if request.method == "POST" and form.validate_on_submit():
        if form.identity_eligible.data == 'yes':
            return local_redirect(url_for('oneLogin.identify'))
        else:
            return local_redirect(url_for('startApplication.reference'))

    return render_template('one-login/identityEligibility.html', form=form)

@oneLogin.route('/onelogin/authenticate', methods=['GET'])
def authenticate():
    config = get_onelogin_config()
    auth = OneLoginAuthorizationRequest(config)
    redirect_url = auth.build_authentication_redirect_url()
    return redirect(redirect_url)

@oneLogin.route('/onelogin/identify', methods=['GET'])
def identify():
    config = get_onelogin_config()
    auth = OneLoginAuthorizationRequest(config)
    redirect_url = auth.build_identity_redirect_url()
    return redirect(redirect_url)

@oneLogin.route('/onelogin/logout', methods=['GET'])
def logout():
    config = get_onelogin_config()
    logout_request = OneLoginLogout(config)
    id_token = session.get('user', {}).get('id_token')

    if id_token is None:
        logger.log(LogLevel.WARN, "ID token not found; redirecting to start")
        logout_request.end_user_session()
        return local_redirect(url_for('oneLogin.start'))

    try:
        redirect_url = logout_request.build_logout_redirect_url(id_token=id_token)
        logout_request.end_user_session()
        return redirect(redirect_url)

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return local_redirect(url_for('oneLogin.start'))

@oneLogin.route('/onelogin/back-channel-logout', methods=['POST'])
def backChannelLogout():
    logger.log(LogLevel.INFO, f'Back channel logout request received.')

    try:
        config = get_onelogin_config()
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
        return Response(status=200) #Still return 200 to let One Login know we received the request

@oneLogin.route('/auth/callback', methods=['GET'])
def callback():
    try:
        if "error" in request.args:
            logger.log(LogLevel.ERROR, f"{request.args['error']} - {request.args.get('error_description', '')}")
            return local_redirect(url_for("oneLogin.start"))

        code = request.args.get("code")
        if not code:
            logger.log(LogLevel.ERROR, "No code received in callback.")
            return local_redirect(url_for("oneLogin.start"))

        handle_onelogin_response(
            code=code,
            fetch_tokens_func=lambda req, c: req.fetch_tokens_auth_request(c),
            store_user_info_func=lambda req, access_token, id_token: req.create_auth_session(access_token, id_token),
        )

        email = session.get('user', {}).get('email')

        if email is None:
            logger.log(LogLevel.INFO, "Could not find email in session.")
            return local_redirect(url_for("oneLogin.start"))

        application = DataStore.create_new_application(email_address=email)
        session['reference_number'] = application.reference_number
        session['lang_code'] = g.lang_code
        DataStore.increment_application_sessions(application.reference_number)

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

        handle_onelogin_response(
            code=code,
            fetch_tokens_func=lambda req, c: req.fetch_tokens_identity_request(c),
            store_user_info_func=lambda req, access_token, id_token: req.update_auth_session_with_identity(access_token, id_token),
        )

        user = session.get('user')

        if user is None:
            logger.log(LogLevel.ERROR, "User session cannot be found on identity proving callback.")
            return local_redirect(url_for("oneLogin.start"))

        name = user.get('name', {})
        address = user.get('address', {})

        application_data = DataStore.load_application_by_session_reference_number()
        application_data.birth_registration_data.date_of_birth = user.get('dob')
        application_data.personal_details_data.first_name = name.get('first_name')
        application_data.personal_details_data.middle_names = name.get('middle_name')
        application_data.personal_details_data.last_name = name.get('last_name')
        application_data.personal_details_data.contact_email_address = user.get('email')
        application_data.personal_details_data.contact_phone_number = user.get('phone_number')
        application_data.personal_details_data.address_line_one = f"{address.get('buildingNumber')} {address.get('streetName')}".strip()
        application_data.personal_details_data.address_town_city = address.get('addressLocality')
        application_data.personal_details_data.address_postcode = address.get('postalCode')
        DataStore.save_application(application_data)

        return local_redirect(url_for("startApplication.reference"))

    except Exception as e:
        logger.log(LogLevel.ERROR, f"Identity callback failed: {str(e)}")
        return local_redirect(url_for("oneLogin.identityEligibility"))

@oneLogin.route('/oneLogin/back-from-email', methods=['GET'])
def backFromEmail():
    session.clear()
    return local_redirect(url_for('oneLogin.start'))

def handle_onelogin_response(code: str, fetch_tokens_func, store_user_info_func):
    config = get_onelogin_config()
    token_request = OneLoginTokenRequest(config)
    token_validator = OneLoginTokenValidator(config)
    user_info_request = OneLoginUserInfoRequest(config)

    access_token, id_token = fetch_tokens_func(token_request, code)
    token_validator.validate_access_id_tokens(access_token=access_token, id_token=id_token)
    store_user_info_func(user_info_request, access_token, id_token)
