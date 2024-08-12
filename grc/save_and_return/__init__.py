from flask import Blueprint, render_template, session
from grc.utils.reference_number import reference_number_string
from grc.utils.decorators import LoginRequired

saveAndReturn = Blueprint('saveAndReturn', __name__)


@saveAndReturn.route('/save-and-return/exit-application', methods=['GET'])
@LoginRequired
def exitApplication():
    response = render_template(
        'save-and-return/exit-application.html',
        reference_number=reference_number_string(session['reference_number'])
    )
    session.clear()
    return response
