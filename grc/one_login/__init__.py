from flask import Blueprint, render_template, request, redirect, session, url_for

from grc.one_login.one_login_logout import OneLoginLogout
from grc.utils.decorators import LoginRequiredOneLogin
from grc.utils.redirect import local_redirect
from grc.one_login.one_login_config import get_onelogin_config
from grc.one_login.one_login_auth_request import OneLoginAuthorizationRequest
from grc.one_login.one_login_token_request import OneLoginTokenRequest
from grc.one_login.one_login_token_validator import OneLoginTokenValidator
from grc.one_login.one_login_user_info_request import OneLoginUserInfoRequest
from grc.utils.logger import LogLevel, Logger

logger = Logger()
oneLogin = Blueprint('oneLogin', __name__)

@oneLogin.route('/home', methods=['GET'])
def index():
    return render_template("one-login/auth.html")

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
        raise Exception("ID token could not be found in session")

    try:
        redirect_url = logout_request.build_logout_redirect_url(id_token=id_token)
        logout_request.end_user_session()
        return redirect(redirect_url)

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return local_redirect(url_for('oneLogin.index'))


@oneLogin.route('/auth/callback', methods=['GET'])
def callback():
    try:
        if "error" in request.args:
            raise Exception(f"{request.args['error']} - {request.args.get('error_description', '')}")

        code = request.args.get("code")
        if not code:
            raise Exception("No code received in callback.")

        return handle_onelogin_callback(
            code=code,
            fetch_tokens_func=lambda req, c: req.fetch_tokens_auth_request(c),
            store_user_info_func=lambda req, access_token, id_token: req.create_auth_session(access_token, id_token),
            success_redirect="oneLogin.userInfo"
        )

    except Exception as e:
        logger.log(LogLevel.ERROR, f"Auth callback failed: {str(e)}")
        return local_redirect(url_for("oneLogin.index"))

@oneLogin.route('/identity/callback', methods=['GET'])
def callbackIdentity():
    try:
        if "error" in request.args:
            raise Exception(f"{request.args['error']} - {request.args.get('error_description', '')}")

        code = request.args.get("code")
        if not code:
            raise Exception("No code received in callback.")

        return handle_onelogin_callback(
            code=code,
            fetch_tokens_func=lambda req, c: req.fetch_tokens_identity_request(c),
            store_user_info_func=lambda req, access_token, id_token: req.update_auth_session_with_identity(access_token, id_token),
            success_redirect="oneLogin.userInfoIdentity"
        )

    except Exception as e:
        logger.log(LogLevel.ERROR, f"Identity callback failed: {str(e)}")
        return local_redirect(url_for("oneLogin.userInfo"))

@oneLogin.route('/userInfo/auth', methods=['GET'])
@LoginRequiredOneLogin
def userInfo():
    return render_template('one-login/userInfoAuth.html')


@oneLogin.route('/userInfo/identity', methods=['GET'])
@LoginRequiredOneLogin
def userInfoIdentity():
    try:
        user = session.get('user')

        if not user:
            raise Exception("User session not found.")

        email = user.get('email')
        phone = user.get('phone_number')
        address = user.get('address', [])
        driving_permit = user.get('driving_permit')
        passport = user.get('passport')
        dob = user.get('dob')
        name = user.get('name')

        address_str = ", ".join([
                                    f"{address_item.get('buildingNumber', '')} {address_item.get('streetName', '')}, {address_item.get('addressLocality', '')}, {address_item.get('postalCode', '')}"
                                    for address_item in address])

        return render_template('one-login/userInfoIdentity.html',
                               email=email,
                               phone=phone,
                               address=address_str,
                               driving_permit=driving_permit,
                               passport=passport,
                               name=name,
                               dob=dob)

    except Exception as e:
        logger.log(LogLevel.ERROR, f"Failed to load user identity page due to error: {str(e)}")
        return local_redirect(url_for('oneLogin.index'))

def handle_onelogin_callback(code: str, fetch_tokens_func, store_user_info_func, success_redirect: str):
    config = get_onelogin_config()
    token_request = OneLoginTokenRequest(config)
    token_validator = OneLoginTokenValidator(config)
    user_info_request = OneLoginUserInfoRequest(config)

    access_token, id_token = fetch_tokens_func(token_request, code)
    token_validator.validate_tokens(access_token=access_token, id_token=id_token)
    store_user_info_func(user_info_request, access_token, id_token)

    return local_redirect(url_for(success_redirect))