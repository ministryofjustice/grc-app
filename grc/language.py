from flask import Blueprint, request, session, redirect

set_language = Blueprint('set_language', __name__)


@set_language.route('/set_language/<lang_code>')
def index(lang_code):
    print(f'{lang_code}', flush=True)
    print("SETTING LANGUAGE")
    session['lang_code'] = lang_code
    print(f'{session}', flush=True)
    return redirect(request.referrer)
