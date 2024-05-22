from flask import Blueprint, render_template, request, session, url_for, flash
from werkzeug.security import generate_password_hash
from admin.admin.forms import SecurityCodeForm
from admin.password_reset.forms import PasswordResetForm
from grc.external_services.gov_uk_notify import GovUkNotify
from grc.models import db, AdminUser
from grc.utils.redirect import local_redirect
from grc.utils.logger import LogLevel, Logger

password_reset = Blueprint('password_reset', __name__)
logger = Logger()


@password_reset.route('/password_reset', methods=['GET', 'POST'])
def index():

    if 'email' not in session:
        logger.log(LogLevel.WARN, f"Forgotten password accessed for no user")
        return local_redirect(url_for('forgot_password.index'))

    form = PasswordResetForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            user = AdminUser.query.filter_by(
                email=session['email']
            ).first()
            user.password = generate_password_hash(form.password.data)
            user.passwordResetRequired = False
            db.session.commit()

            logger.log(LogLevel.INFO, f"{logger.mask_email_address(session['email'])} reset their password")

            return render_template('password_reset/password-has-been-reset.html')

    return render_template(
        'password_reset/password_reset.html',
        form=form
    )


@password_reset.route('/reset-password-with-security-code', methods=['GET', 'POST'])
def reset_password_security_code():
    form = SecurityCodeForm()
    email_address = session['email']

    # 2FA link
    if request.method == 'POST':
        if form.validate_on_submit():

            user = AdminUser.query.filter_by(
                email=email_address
            ).first()

            if user is None:
                message = "We could not find your user details. Please try resetting your password again"
                return render_template('password_reset/password-reset-link-error.html', message=message)

            logger.log(LogLevel.INFO, f"User {logger.mask_email_address(email_address)} logged in with security code")
            session['email'] = email_address
            return local_redirect(url_for('password_reset.index'))

    if request.method == 'GET' and request.args.get('resend') == 'true':
        GovUkNotify().send_email_admin_login_security_code(session['email'])
        flash('We’ve resent you a security code. This can take a few minutes to arrive.', 'email')
    return render_template(
        'password_reset/password-reset-security-code.html',
        form=form
    )
