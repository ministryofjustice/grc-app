import random, string
from flask import Blueprint, render_template, request, session
from werkzeug.security import generate_password_hash
from grc.utils.decorators import AdminRequired
from admin.users.forms import UsersForm
from grc.external_services.gov_uk_notify import GovUkNotify
from grc.models import db, AdminUser
from grc.utils.logger import LogLevel, Logger

users = Blueprint('users', __name__)
logger = Logger()


@users.route('/users', methods=['GET'])
@AdminRequired
def index():
    users = AdminUser.query.all()

    return render_template(
        'users/users.html',
        users=users
    )


@users.route('/users/invite-new-admin-user', methods=['GET', 'POST'])
@AdminRequired
def invite_new_admin_user():
    form = UsersForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            email_address: str = form.email_address.data
            email_address = email_address.lower()
            user = AdminUser.query.filter_by(
                email=email_address
            ).first()

            if user is not None:
                form.email_address.errors.append("A user account with that email address already exists")
                logger.log(LogLevel.WARN, f"{logger.mask_email_address(session['signedIn'])} attempted to create an account for {email_address} which already exists")
            else:
                temporary_password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
                userType = 'ADMIN' if form.is_admin_user.data else 'VIEWER'
                record = AdminUser(email=email_address, password=generate_password_hash(temporary_password), userType=userType)
                db.session.add(record)
                db.session.commit()

                try:
                    GovUkNotify().send_email_admin_new_user(
                        email_address=email_address,
                        temporary_password=temporary_password,
                        application_link=request.host_url
                    )
                except Exception as e:
                    logger.log(LogLevel.ERROR, str(e))

                logger.log(LogLevel.WARN, f"{logger.mask_email_address(session['signedIn'])} created an account for {email_address}")

                return render_template(
                    'users/invite-sent.html',
                    email_address=email_address,
                )

    return render_template(
        'users/invite-new-user.html',
        form=form
    )


@users.route('/users/<emailAddress>/delete', methods=['GET', 'POST'])
@AdminRequired
def delete(emailAddress):
    user = AdminUser.query.filter_by(
        email=emailAddress
    ).first()
    number_of_admin_users = AdminUser.query.filter_by(
        userType='ADMIN'
    ).count()

    if user is None:
        logger.log(LogLevel.WARN, f"{logger.mask_email_address(session['signedIn'])} attempted to delete an account for {emailAddress} which does not exist")

        return render_template(
            'users/user-delete-failed-user-not-found.html',
            email_address=emailAddress
        )

    elif number_of_admin_users == 1 and user.userType == 'ADMIN':
        logger.log(LogLevel.WARN, f"{logger.mask_email_address(session['signedIn'])} attempted to delete the last admin account for {emailAddress}")

        return render_template('users/user-delete-failed-cannot-delete-last-admin-user.html')

    else:
        if request.method == 'POST':
            db.session.delete(user)
            db.session.commit()
            logger.log(LogLevel.WARN, f"{logger.mask_email_address(session['signedIn'])} deleted account for {emailAddress}")

            return render_template(
                'users/user-deleted.html',
                email_address=emailAddress
            )

        else:
            return render_template(
                'users/delete-user.html',
                email_address=emailAddress
            )


@users.route('/users/<emailAddress>/resend', methods=['GET'])
@AdminRequired
def resend(emailAddress):
    user = AdminUser.query.filter_by(
        email=emailAddress
    ).first()

    if user is None:
        logger.log(LogLevel.WARN, f"{logger.mask_email_address(session['signedIn'])} attempted to resend an invite for {emailAddress} which does not exist")

        return render_template(
            'users/invite-resend-failed-user-not-found.html',
            email_address=emailAddress
        )

    elif user.dateLastLogin is not None:
        logger.log(LogLevel.WARN, f"{logger.mask_email_address(session['signedIn'])} attempted to create an account for {emailAddress} which has already been created")

        return render_template(
            'users/invite-resend-failed-already-logged-in.html',
            email_address=emailAddress
        )

    else:
        temporary_password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        user.password = generate_password_hash(temporary_password)
        db.session.commit()
        logger.log(LogLevel.WARN, f"{logger.mask_email_address(session['signedIn'])} sent an invite to {emailAddress}")

        try:
            GovUkNotify().send_email_admin_new_user(
                email_address=user.email,
                temporary_password=temporary_password,
                application_link=request.host_url
            )
        except Exception as e:
            logger.log(LogLevel.ERROR, str(e))

        return render_template(
            'users/invite-resent.html',
            email_address=emailAddress
        )
