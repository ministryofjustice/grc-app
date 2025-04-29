from flask import Blueprint, render_template, request, redirect, session, url_for
from grc.one_login.one_login_config import OneLoginConfig
from grc.one_login.one_login_auth_request import OneLoginAuthorizationRequest
from grc.one_login.one_login_token_request import OneLoginTokenRequest
from grc.one_login.one_login_token_storage import OneLoginTokenStorage
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
    config = OneLoginConfig()
    auth = OneLoginAuthorizationRequest(config)
    signed_jwt = auth.create_signed_auth_request(vtr="Cl.Cm")
    redirect_url = auth.build_redirect_url(signed_jwt)
    return redirect(redirect_url)

@oneLogin.route('/onelogin/identify', methods=['GET'])
def identify():
    config = OneLoginConfig()
    auth = OneLoginAuthorizationRequest(config)
    signed_jwt = auth.create_signed_auth_request(vtr="Cl.Cm.P2")
    redirect_url = auth.build_redirect_url(signed_jwt)
    return redirect(redirect_url)

@oneLogin.route('/auth/callback', methods=['GET'])
def callback():
    try:
        if "error" in request.args:
            error = request.args["error"]
            error_desc = request.args.get("error_description", "")
            error_message = f"{str(error)} - {str(error_desc)}"
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

        code = request.args.get("code")

        if not code:
            error_message = "No code received in callback."
            logger.log(LogLevel.ERROR, error_message)
            raise Exception(error_message)

        config = OneLoginConfig()
        token_request = OneLoginTokenRequest(config)
        token_validator = OneLoginTokenValidator(config)

        access_token, id_token = token_request.fetch_tokens(code)
        token_validator.validate_tokens(access_token=access_token, id_token=id_token)
        OneLoginTokenStorage.store_tokens(access_token=access_token, id_token=id_token)

        return redirect(url_for("oneLogin.userInfo"))

    except Exception as e:
        logger.log(LogLevel.ERROR, f"Callback failure due to {str(e)}")
        return redirect(url_for("oneLogin.index"))

@oneLogin.route('/userInfo', methods=['GET'])
def userInfo():
    config = OneLoginConfig()
    user_info_request = OneLoginUserInfoRequest(config)

    user_info = user_info_request.fetch_user_info()
    email = user_info.get('email')
    phone = user_info.get('phone_number')

    return render_template('one-login/userInfo.html', email=email, phone=phone)
