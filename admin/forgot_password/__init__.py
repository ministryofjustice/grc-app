from datetime import datetime, timedelta
from dateutil import tz
from flask import Blueprint, render_template, request, session, url_for
from admin.forgot_password.forms import ForgotPasswordForm
from grc.external_services.gov_uk_notify import GovUkNotify
from grc.models import AdminUser
from grc.utils.logger import LogLevel, Logger
from grc.utils.security_code import _security_code_generator
from grc.utils.redirect import local_redirect

forgot_password = Blueprint('forgot_password', __name__)
logger = Logger()


@forgot_password.route('/forgot_password', methods=['GET', 'POST'])
def index():
    form = ForgotPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        email_address: str = form.email_address.data.lower()
        user = AdminUser.query.filter_by(email=email_address).first()

        if user is not None:
            try:
                GovUkNotify().send_email_admin_forgot_password(email_address=user.email)
                logger.log(LogLevel.INFO, f"Password reset link sent to {logger.mask_email_address(email_address)}")
            except Exception as e:
                logger.log(LogLevel.ERROR, str(e))
        else:
            logger.log(LogLevel.WARN, f"Password reset requested for unknown user {logger.mask_email_address(email_address)}")

        session['email'] = email_address
        return local_redirect(url_for('password_reset.reset_password_security_code'))

    return render_template(
        'forgot-password/forgot_password.html',
        form=form
    )
