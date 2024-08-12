def test_language_toggle_welsh(app, client):
    with app.app_context():
        response = client.get('/')
        assert response.status_code == 200

        with client.session_transaction() as session:
            session['lang_code'] = 'en'

        headers = {'Referer': '/'}
        response = client.get('/set_language/cy', headers=headers)
        assert response.status_code == 302

        with client.session_transaction() as session:
            assert session.get('lang_code') == 'cy'


def test_language_toggle_english(app, client):
    with app.app_context():
        response = client.get('/')
        assert response.status_code == 200

        with client.session_transaction() as session:
            session['lang_code'] = 'cy'

        headers = {'Referer': '/'}
        response = client.get('/set_language/en', headers=headers)
        assert response.status_code == 302

        with client.session_transaction() as session:
            assert session.get('lang_code') == 'en'
