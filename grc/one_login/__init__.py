from flask import Blueprint, render_template, request, redirect, session, url_for, Response, g, flash, get_flashed_messages
from grc.one_login.one_login_logout import OneLoginLogout
from grc.utils.decorators import UnverifiedLoginRequired, LoginRequired, Unauthorized, AfterOneLogin
from grc.utils.redirect import local_redirect
from grc.one_login.one_login_config import OneLoginConfig
from grc.one_login.one_login_auth_request import OneLoginAuthorizationRequest
from grc.one_login.one_login_token_request import OneLoginTokenRequest
from grc.one_login.one_login_token_validator import OneLoginTokenValidator
from grc.one_login.one_login_user_info_request import OneLoginUserInfoRequest
from grc.utils.logger import LogLevel, Logger
from grc.one_login.forms import ReferenceCheckForm, NewExistingApplicationForm
from grc.business_logic.data_store import DataStore
from grc.models import Application, ApplicationStatus
from grc.utils.strtobool import strtobool

logger = Logger()
oneLogin = Blueprint('oneLogin', __name__)

@oneLogin.route('/', methods=['GET', 'POST'])
@Unauthorized
def start():
    form = NewExistingApplicationForm()
    if request.method == "POST" and form.validate_on_submit():
        session.permanent = True
        new_application = strtobool(form.new_application.data)
        if new_application is True:
            session['one_login_auth'] = True
            return local_redirect(url_for('oneLogin.authenticate'))
        else:
            return local_redirect(url_for('oneLogin.referenceNumber'))
    return render_template('one-login/start.html', form=form)

@oneLogin.route('/your-reference-number', methods=['GET', 'POST'])
@Unauthorized
def referenceNumber():
    form = ReferenceCheckForm()
    has_reference = form.has_reference.data

    if session.get('reference_number_unverified'):
        session.pop('reference_number_unverified')
    if request.method == "POST" and form.validate_on_submit():
        if has_reference == 'HAS_REFERENCE':
            reference = DataStore.compact_reference(form.reference.data)
            application = Application.query.filter_by(reference_number=reference).first()

            if application.status == ApplicationStatus.DELETED or application.status == ApplicationStatus.ABANDONED:
                return render_template('start-application/application-anonymised.html')

            elif application.status == ApplicationStatus.COMPLETED or \
                    application.status == ApplicationStatus.SUBMITTED or \
                    application.status == ApplicationStatus.DOWNLOADED:
                return render_template('start-application/application-already-submitted.html')

            else:
                application_data = application.application_data()
                session['reference_number_unverified'] = reference

                if application_data.created_after_one_login:
                    session['one_login_auth'] = True
                    logger.log(LogLevel.INFO, f"Application with reference number {str(reference)} was created AFTER One Login implementation. Redirecting to One Login.")
                    return redirect(url_for('oneLogin.authenticate'))
                else:
                    session['one_login_auth'] = False
                    logger.log(LogLevel.INFO, f"Application with reference number {str(reference)} was created BEFORE One Login implementation. Redirecting to original auth.")
                    return local_redirect(url_for('startApplication.index'))

        elif has_reference == 'LOST_REFERENCE':
            return local_redirect(url_for('oneLogin.start'))

    return render_template('one-login/referenceNumber.html', form=form)

@oneLogin.route('/one-login/authenticate', methods=['GET'])
def authenticate():
    config = OneLoginConfig.get_instance()
    auth = OneLoginAuthorizationRequest(config)
    redirect_url = auth.build_authentication_redirect_url()
    return redirect(redirect_url)

@oneLogin.route('/one-login/logout', methods=['GET'])
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

@oneLogin.route('/one-login/auth/callback', methods=['GET'])
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
        reference_number_unverified = session.get('reference_number_unverified')

        if reference_number_unverified:
            session['reference_number'] = reference_number_unverified
            application_data = DataStore.load_application_by_session_reference_number()
            if email != application_data.email_address:
                flash('There is a mismatch with your application reference number and GOV.UK One Login email address', "error")
                logout_request = OneLoginLogout(OneLoginConfig.get_instance())
                redirect_url = logout_request.logout_redirect_url_to_reference_check_page(id_token)
                session.pop('reference_number')
                logger.log(LogLevel.ERROR, "Email address does not match our records for the reference number you provided.")
                return local_redirect(redirect_url)

        else:
            application_data = DataStore.create_new_application(email_address=email)
            session['reference_number'] = application_data.reference_number
            DataStore.increment_application_sessions(application_data.reference_number)

        DataStore.save_application(application_data)

        user_info_request.store_user_info_redis_mapping(sub)

        return local_redirect(url_for("startApplication.reference"))

    except Exception as e:
        logger.log(LogLevel.ERROR, f"Auth callback failed: {str(e)}")
        return local_redirect(url_for("oneLogin.start"))

@oneLogin.route('/back-from-reference', methods=['GET'])
def backFromReference():
    session.clear()
    return local_redirect(url_for('oneLogin.start'))

