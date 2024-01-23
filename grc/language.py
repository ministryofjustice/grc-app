from flask import Blueprint, request, session, redirect

set_language = Blueprint('set_language', __name__)


@set_language.route('/set_language/<lang_code>')
def index(lang_code):
    session['lang_code'] = lang_code
    return redirect(request.referrer)
