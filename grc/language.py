from flask import Blueprint, request, session
from .utils.redirect import local_redirect

set_language = Blueprint('set_language', __name__)


@set_language.route('/set_language/<lang_code>', methods=['GET'])
def index(lang_code):
    session['lang_code'] = lang_code
    return local_redirect(request.referrer)
