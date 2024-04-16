import random
import string
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, url_for, current_app, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from admin.admin.forms import LoginForm, SecurityCodeForm
from grc.external_services.gov_uk_notify import GovUkNotify
from grc.models import db, AdminUser, SecurityCode
from grc.utils.date_utils import convert_date_to_local_timezone
from grc.utils.redirect import local_redirect
from grc.utils.logger import LogLevel, Logger
from grc.utils.security_code import generate_security_code, send_security_code_admin, \
    has_last_security_code_been_used, has_security_code_expired

admin = Blueprint('admin', __name__)
logger = Logger()


@admin.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if 'signedIn' in session:
        return local_redirect(url_for('applications.index'))

    if request.method == 'POST':
        if form.validate_on_submit():
            email_address: str = form.email_address.data
            email_address = email_address.lower()
            user = AdminUser.query.filter_by(
                email=email_address
            ).first()

            if not user:
                form.email_address.errors.append("A user with this email address was not found")
                session.pop('signedIn', None)
                session.pop('email', None)
                session.pop('userType', None)
                logger.log(LogLevel.WARN, f"User {logger.mask_email_address(email_address)} not found")
                return render_template('login/login.html', form=form)

            if not check_password_hash(user.password, form.password.data):
                form.password.errors.append("Your password was incorrect. Please try re-entering your password")
                logger.log(LogLevel.INFO, f"{logger.mask_email_address(email_address)} entered incorrect password")
                return render_template('login/login.html', form=form)

            session['email'] = email_address
            session['userType'] = user.userType

            if user.passwordResetRequired:
                logger.log(LogLevel.INFO, f"{logger.mask_email_address(email_address)} password reset required")
                return local_redirect(url_for('password_reset.index'))

            now_local = convert_date_to_local_timezone(datetime.now())
            security_code = SecurityCode.query.filter_by(email=email_address).first()

            if security_code and user.dateLastLogin:
                security_code_created_local = convert_date_to_local_timezone(security_code.created)
                security_code_expiry_date = security_code_created_local + timedelta(hours=24)

                last_logged_in_local = convert_date_to_local_timezone(
                    datetime.strptime(user.dateLastLogin, '%d/%m/%Y %H:%M:%S')
                )

                last_security_code_has_been_used = has_last_security_code_been_used(
                    last_logged_in_local, security_code_created_local
                )

                security_code_has_expired = has_security_code_expired(security_code_expiry_date, now_local)

                if not security_code_has_expired and last_security_code_has_been_used:
                    logger.log(LogLevel.INFO, f"Security code hasn't expired and" 
                                              f" user ({logger.mask_email_address(email_address)}) last logged in"
                                              f" ({last_logged_in_local.date()}, {last_logged_in_local.time()}) "
                                              f"and last security code created at {security_code_created_local.date()}"
                                              f", {security_code_created_local.time()} has been used. No security "
                                              f"code required")

                    user.dateLastLogin = datetime.strftime(now_local, '%d/%m/%Y %H:%M:%S')
                    db.session.commit()
                    session['signedIn'] = email_address
                    return local_redirect(url_for('applications.index'))

            # Email out 2FA link
            security_code, expires = generate_security_code(email_address)
            GovUkNotify().send_email_admin_login_security_code(email_address=user.email, expires=expires,
                                                               security_code=security_code)
            logger.log(LogLevel.INFO, f"login link sent to {logger.mask_email_address(user.email)}")
            return local_redirect(url_for('admin.sign_in_with_security_code'))

    else:
        add_default_admin_user_to_database_if_there_are_no_users()

    return render_template('login/login.html', form=form)


@admin.route('/sign-in-with-security_code', methods=['GET', 'POST'])
def sign_in_with_security_code():
    form = SecurityCodeForm()
    email_address = session['email']

    # 2FA link
    if request.method == 'POST':
        if form.validate_on_submit():

            user = AdminUser.query.filter_by(email=email_address).first()

            if user is None:
                message = "We could not find your user details. Please try logging in again"
                return render_template('login/login-security-code-error.html', message=message)

            local = convert_date_to_local_timezone(datetime.now())
            user.dateLastLogin = datetime.strftime(local, '%d/%m/%Y %H:%M:%S')
            db.session.commit()

            session['signedIn'] = email_address
            session['userType'] = user.userType

            logger.log(LogLevel.INFO, f"User {logger.mask_email_address(email_address)} logged in with security code")
            return local_redirect(url_for('applications.index'))

    if request.method == 'GET' and request.args.get('resend') == 'true':
        try:
            send_security_code_admin(session['email'])
            flash('We’ve resent you a security code. This can take a few minutes to arrive.', 'email')
        except BaseException as err:
            error = err.args[0].json()
            flash(error['errors'][0]['message'], 'error')

    return render_template('login/login-security-code-sent.html', email_address=email_address, form=form)


def add_default_admin_user_to_database_if_there_are_no_users():
    number_of_admins = db.session.query(AdminUser).count()
    if number_of_admins == 0:
        default_email_address: str = current_app.config['DEFAULT_ADMIN_USER']
        default_email_address = default_email_address.lower()
        temporary_password = generate_temporary_password()
        record = AdminUser(email=default_email_address, password=generate_password_hash(temporary_password),
                           userType='ADMIN')
        db.session.add(record)
        db.session.commit()

        try:
            GovUkNotify().send_email_admin_new_user(
                email_address=default_email_address,
                temporary_password=temporary_password,
                application_link=request.base_url
            )
        except Exception as e:
            logger.log(LogLevel.ERROR, message=f'{e}')


def generate_temporary_password():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
