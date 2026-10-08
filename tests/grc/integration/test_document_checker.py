"""Service-free checker routes; the runner supplies synthetic config before collection.

Compile the candidate Welsh catalogue before starting pytest. C3 and C7 use the
approved Welsh wording, retaining the existing new-tab warning in the C3 link.
"""

from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from xml.etree.ElementTree import Element, SubElement

import jsonpickle
import pytest
import requests
from babel.messages.pofile import read_po
from flask import g, session
from flask.sessions import SecureCookieSessionInterface
from flask.testing import FlaskClient
from sqlalchemy.engine import Engine

import grc
import grc.document_checker as checker
import grc.external_services.gov_uk_notify as notify_service
from grc.business_logic.constants.document_checker import DocumentCheckerConstants
from grc.business_logic.data_store import DataStore
from grc.document_checker.doc_checker_state import (
    CurrentlyInAPartnershipEnum as Partnership,
    DocCheckerState,
)
from grc.external_services.aws_s3_client import AwsS3Client
from grc.one_login.one_login_config import OneLoginConfig


ORIGIN = 'https://checker.example.test'
STATE_KEY = 'documentCheckerState'
EMAIL = 'checker.recipient@example.com'
PATHS = {
    'start': '/check-documents',
    'name': '/check-documents/changed-name-to-reflect-gender',
    'relationship': '/check-documents/currently-in-a-partnership',
    'remain': '/check-documents/plan-to-remain-in-a-partnership',
    'died': '/check-documents/previous-partnership-partner-died',
    'ended': '/check-documents/previous-partnership-ended',
    'overseas': '/check-documents/gender-recognition-outside-uk',
    'results': '/check-documents/your-documents',
    'email': '/check-documents/email-address',
    'sent': '/check-documents/email-sent',
}
FIELDS = {
    'name': 'changed_name_to_reflect_gender',
    'relationship': 'currently_in_a_partnership',
    'remain': 'plan_to_remain_in_a_partnership',
    'died': 'previous_partnership_partner_died',
    'ended': 'previous_partnership_ended',
    'overseas': 'gender_recognition_outside_uk',
}

# Independent literals, not gettext or properties obtained from the subject under test.
SUMMARY_TEXT = {
    'name_change_documents': (
        'Copies of all change of name documents', "Cop\u00efau o'r holl ddogfennau newid enw"),
    'medical_reports': ('Medical reports', 'Adroddiadau meddygol'),
    'evidence_of_living_in_gender': (
        'Evidence of living in your affirmed gender for 2 years',
        'Tystiolaeth eich bod wedi byw yn eich rhywedd a gadarnhawyd am 2 flynedd'),
    'statutory_declaration_for_single_applicant': (
        'Statutory declaration for single applicants', 'Datganiad statudol ar gyfer ceiswyr sengl'),
    'statutory_declaration_for_married_applicant': (
        'Statutory declaration for applicants who are married',
        'Datganiad statudol ar gyfer ceiswyr sy\u2019n briod'),
    'statutory_declaration_for_applicant_in_civil_partnership': (
        'Statutory declaration for applicants who are in a civil partnership',
        'Datganiad statudol ar gyfer ceiswyr sydd mewn partneriaeth sifil'),
    'spouses_statutory_declaration': (
        'Your spouse\u2019s statutory declaration', 'Datganiad statudol eich priod'),
    'civil_partners_statutory_declaration': (
        'Your civil partner\u2019s statutory declaration', 'Datganiad statudol eich partner sifil'),
    'marriage_certificate': ('Your marriage certificate', 'Eich tystysgrif priodas'),
    'civil_partnership_certificate': (
        'Your civil partnership certificate', 'Eich tystysgrif partneriaeth sifil'),
    'death_certificate': (
        'Death certificate for your spouse or civil partner',
        'Tystysgrif marwolaeth ar gyfer eich priod neu bartner sifil'),
    'decree_absolute': (
        'Decree absolute or final order', 'Dyfarniad absoliwt neu orchymyn terfynol'),
    'proof_gender_recognised_outside_uk': (
        'Proof that your affirmed gender is recognised outside the UK',
        "Prawf bod eich rhywedd a gadarnhawyd yn cael ei gydnabod y tu allan i'r DU"),
}
AGGREGATE_FLAGS = {
    'statutory_declaration_for_applicant_in_partnership',
    'partners_statutory_declaration',
    'partnership_certificate',
}
MARRIED = {
    'statutory_declaration_for_applicant_in_partnership', 'partnership_certificate',
    'statutory_declaration_for_married_applicant', 'marriage_certificate',
}
CIVIL = {
    'statutory_declaration_for_applicant_in_partnership', 'partnership_certificate',
    'statutory_declaration_for_applicant_in_civil_partnership', 'civil_partnership_certificate',
}
SINGLE = {'statutory_declaration_for_single_applicant'}
RELATIONSHIP_CASES = [
    pytest.param(Partnership.MARRIED, True, None, None,
                 MARRIED | {'partners_statutory_declaration', 'spouses_statutory_declaration'},
                 id='married-remain'),
    pytest.param(Partnership.MARRIED, False, None, None, MARRIED, id='married-leave'),
    pytest.param(Partnership.CIVIL_PARTNERSHIP, True, None, None,
                 CIVIL | {'partners_statutory_declaration', 'civil_partners_statutory_declaration'},
                 id='civil-remain'),
    pytest.param(Partnership.CIVIL_PARTNERSHIP, False, None, None, CIVIL, id='civil-leave'),
    pytest.param(Partnership.NEITHER, None, False, False, SINGLE, id='single'),
    pytest.param(Partnership.NEITHER, None, True, False,
                 SINGLE | {'death_certificate'}, id='bereaved'),
    pytest.param(Partnership.NEITHER, None, False, True,
                 SINGLE | {'decree_absolute'}, id='ended'),
    pytest.param(Partnership.NEITHER, None, True, True,
                 SINGLE | {'death_certificate', 'decree_absolute'}, id='bereaved-and-ended'),
]

CERTIFY_URL = 'https://www.gov.uk/certifying-a-document'
ORDER_URL = 'https://www.gov.uk/order-copy-birth-death-marriage-certificate'
POSTAL_FALLBACK = 'If you cannot upload your certificate, post it after you submit your application.'
COPY = {
    'en': {
        'certify_link': 'certified copy (opens in a new tab)',
        'source_quality': (
            'Use the original or a certified copy (opens in a new tab) '
            'of your full birth or adoption certificate.'),
        'postal_fallback': POSTAL_FALLBACK,
        'upload': 'Documents to upload',
        'certificate': 'Birth or adoption certificate',
        'translation': 'If any of your documents are not in English',
        'email': 'Get this list by email',
        'intro': (
            'You can upload most documents online, including your birth or adoption certificate. '
            'You can also post your birth or adoption certificate to us if you cannot upload it.'),
        'guidance': (
            'You can upload a scan or good quality photograph of your full birth or adoption certificate.',
            'If you upload your certificate, you do not need to post it to us unless we ask you to.',
            'If you have an adoption certificate, upload that instead of your birth certificate.'),
        'order_link': 'order a certificate (opens in a new tab)',
        'order': (
            'If your birth or adoption was registered in the UK, find out how to '
            'order a certificate (opens in a new tab) if you do not have it available.'),
        'originals': 'You\u2019ll need to send in both the original documents and the translations.',
        'email_errors': ('Enter your email address', 'Enter a valid email address'),
    },
    'cy': {
        'certify_link': 'neu ardystiedig (yn agor mewn tab newydd)',
        'source_quality': (
            'Defnyddiwch gopi gwreiddiol neu ardystiedig (yn agor mewn tab newydd) '
            "o'ch tystysgrif geni neu fabwysiadu llawn."),
        'postal_fallback': (
            'Os na allwch uwchlwytho eich tystysgrif, postiwch hi ar ôl cyflwyno eich cais.'),
        'upload': "Dogfennau i'w llwytho",
        'certificate': 'Tystysgrif geni neu fabwysiadu',
        'translation': "Os nad yw unrhyw un o'ch dogfennau yn Saesneg",
        'email': 'Cael y rhestr hon drwy e-bost',
        'intro': (
            "Gallwch uwchlwytho'r rhan fwyaf o ddogfennau ar-lein, gan gynnwys eich tystysgrif "
            "geni neu fabwysiadu. Gallwch hefyd bostio'ch tystysgrif geni neu fabwysiadu atom "
            'os na allwch ei huwchlwytho.'),
        'guidance': (
            "Gallwch uwchlwytho sgan neu lun o ansawdd da o'ch tystysgrif geni neu fabwysiadu lawn.",
            'Os byddwch yn uwchlwytho eich tystysgrif, nid oes angen i chi ei phostio atom '
            'oni bai ein bod yn gofyn i chi wneud hynny.',
            'Os oes gennych dystysgrif mabwysiadu, uwchlwythwch honno yn lle eich tystysgrif geni.'),
        'order_link': 'hyd i wybodaeth am sut i archebu tystysgrif (yn agor mewn tab newydd)',
        'order': (
            'Os cafodd eich genedigaeth neu eich mabwysiad ei chofrestru yn y DU, dewch o '
            'hyd i wybodaeth am sut i archebu tystysgrif (yn agor mewn tab newydd) '
            'os nad oes gennych un wrth law.'),
        'originals': "Bydd angen i chi anfon y dogfennau gwreiddiol a'r cyfieithiadau atom.",
        'email_errors': ('Nodwch eich cyfeiriad e-bost', 'Nodwch gyfeiriad e-bost dilys'),
    },
}


class _HTML(HTMLParser):
    """Small stdlib tree adapter for these pages, retaining sibling order and text."""

    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
            'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Element('document')
        self.stack = [self.root]
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = SubElement(self.stack[-1], tag, {key: value or '' for key, value in attrs})
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        parent = self.stack[-1]
        if len(parent):
            parent[-1].tail = (parent[-1].tail or '') + data
        else:
            parent.text = (parent.text or '') + data


def _text(node):
    return ' '.join(''.join(node.itertext()).split())


def _elements(node, tag, css_class=None):
    return [item for item in node.iter(tag)
            if css_class is None or css_class in item.get('class', '').split()]


def _one(items):
    assert len(items) == 1
    return items[0]


def _page(response):
    assert response.status_code == 200
    assert response.request.url.startswith(ORIGIN + '/')
    return _HTML(response.get_data(as_text=True)).root


def _main(page):
    return _one(page.findall(".//main[@id='main-content']"))


def _summary(details):
    return _text(_one(details.findall('summary')))


def _saved_session(client):
    with client.session_transaction(base_url=ORIGIN) as saved:
        return dict(saved)


def _saved_answers(client):
    state = jsonpickle.decode(_saved_session(client)[STATE_KEY])
    return {field: getattr(state, field) for field in FIELDS.values()}


def _answers(relationship=Partnership.NEITHER, remain=None, died=False, ended=False,
             changed=False, overseas=False):
    return {FIELDS['name']: changed, FIELDS['relationship']: relationship,
            FIELDS['remain']: remain, FIELDS['died']: died,
            FIELDS['ended']: ended, FIELDS['overseas']: overseas}


def _expected_flags(required, changed, overseas):
    expected = set(required)
    if changed:
        expected.add('name_change_documents')
    expected.update({'proof_gender_recognised_outside_uk'} if overseas else
                    {'medical_reports', 'evidence_of_living_in_gender'})
    return {'need_to_send_' + name: name in expected
            for name in SUMMARY_TEXT.keys() | AGGREGATE_FLAGS}


def _assert_summaries(main, locale, required, changed=False, overseas=False):
    flags = _expected_flags(required, changed, overseas)
    index = 0 if locale == 'en' else 1
    expected = {labels[index] for name, labels in SUMMARY_TEXT.items()
                if flags['need_to_send_' + name]}
    expected.add(COPY[locale]['certificate'])
    summaries = [_summary(item) for item in _elements(main, 'details', 'govuk-details')]
    assert len(summaries) == len(expected)
    assert set(summaries) == expected


def _assert_certificate(main, locale):
    copy = COPY[locale]
    details = _elements(main, 'details', 'govuk-details')
    certificate = _one([item for item in details if _summary(item) == copy['certificate']])
    assert details[-1] is certificate
    parent = next(node for node in main.iter() if certificate in list(node))
    siblings = list(parent)
    position = siblings.index(certificate)
    preceding = [node for node in siblings[:position] if node.tag == 'h2']
    following = [node for node in siblings[position + 1:] if node.tag == 'h2']
    assert preceding and _text(preceding[-1]) == copy['upload']
    assert following and _text(following[0]) == copy['translation']
    # Also rejects an empty/orphan postal heading, without counting page-wide phrases.
    assert [_text(node) for node in main.iter('h2')] == [
        copy['upload'], copy['translation'], copy['email']]
    assert copy['intro'] in [_text(node) for node in parent.findall('p')]
    assert all(_text(node).rstrip('.') !=
               'You should post the following documents after you have submitted your application'
               for node in main.iter('p'))
    body = _one(_elements(certificate, 'div', 'govuk-details__text'))
    assert [_text(node) for node in body.findall('p')] == [
        copy['source_quality'], *copy['guidance'], copy['postal_fallback'], copy['order']]
    links = list(body.iter('a'))
    assert [(link.get('href'), _text(link), link.get('target')) for link in links] == [
        (CERTIFY_URL, copy['certify_link'], '_blank'), (ORDER_URL, copy['order_link'], '_blank')]
    assert links[0].get('rel') == 'external'
    # C9 was not selected: keep the existing translation requirement unchanged.
    assert copy['originals'] in [_text(node) for node in parent.findall('p')]
    assert len(main.findall(".//a[@href='/email']")) == 1
    form = _one(main.findall(".//form[@action='/check-documents/email-address']"))
    assert form.get('method').lower() == 'get'
    assert len(form.findall('button')) == 1


@pytest.fixture(autouse=True)
def no_external_io(monkeypatch):
    attempts = []

    def forbidden(*args, **kwargs):
        attempts.append('unexpected external/application boundary')
        pytest.fail('Checker must not use HTTP, SQL, S3, One Login or an application record')

    monkeypatch.setattr(requests.sessions.Session, 'request', forbidden)
    monkeypatch.setattr(Engine, 'connect', forbidden)
    monkeypatch.setattr(AwsS3Client, '__init__', forbidden)
    monkeypatch.setattr(OneLoginConfig, 'get_instance', classmethod(forbidden))
    monkeypatch.setattr(notify_service, 'NotificationsAPIClient', forbidden)
    monkeypatch.setattr(checker, 'GovUkNotify', forbidden)
    for name in ('load_application', 'load_application_by_session_reference_number',
                 'create_new_application', 'save_application'):
        monkeypatch.setattr(DataStore, name, staticmethod(forbidden))
    yield
    # Do not let a production broad exception handler turn a forbidden attempt into a pass.
    assert attempts == []


class _HTTPSClient(FlaskClient):
    def open(self, *args, **kwargs):
        kwargs.setdefault('base_url', ORIGIN)
        return super().open(*args, **kwargs)


@pytest.fixture
def app(monkeypatch, no_external_io):
    class CheckerTestConfig(grc.TestConfig):
        TESTING = True
        SECRET_KEY = 'synthetic-checker-tests-only'
        WTF_CSRF_ENABLED = False
        ENVIRONMENT = 'test'
        FLASK_ENV = 'test'
        FLASK_APP = 'grc'
        MAINTENANCE_MODE = 'OFF'
        BASIC_AUTH_USERNAME = ''
        BASIC_AUTH_PASSWORD = ''
        MEMORY_STORAGE_URL = None
        REDIS_HOST = 'redis.invalid'
        AV_API = None
        SERVER_NAME = 'checker.example.test'
        PREFERRED_URL_SCHEME = 'https'
        BASE_URL = ORIGIN + '/'

    # The factory consumes its imported alias, not the identity of its truthy argument.
    monkeypatch.setattr(grc, 'TestConfig', CheckerTestConfig)
    monkeypatch.setattr(grc, 'Session', lambda app: None)
    monkeypatch.setattr(grc.redis, 'Redis', lambda *args, **kwargs: object())
    for extension in (grc.cache, grc.db, grc.migrate):
        monkeypatch.setattr(extension, 'init_app', lambda *args, **kwargs: None)
    monkeypatch.chdir(Path(__file__).resolve().parents[3])
    application = grc.create_app(True)
    assert grc.limiter.limiter(application) is None
    application.session_interface = SecureCookieSessionInterface()
    application.test_client_class = _HTTPSClient
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seed_checker_state(client):
    def seed(answers, locale='en'):
        state = DocCheckerState()
        for field, value in answers.items():
            assert field in FIELDS.values()
            setattr(state, field, value)
        with client.session_transaction(base_url=ORIGIN) as saved:
            saved.clear()
            saved[STATE_KEY] = jsonpickle.encode(state)
            saved['lang_code'] = locale
    return seed


@pytest.fixture
def checker_notify(monkeypatch):
    calls = []

    def record(*, email_address, documents_required):
        calls.append((g.lang_code, session['lang_code'], email_address, deepcopy(documents_required)))

    send = Mock(side_effect=record)
    factory = Mock(return_value=SimpleNamespace(
        send_email_documents_you_need_for_your_grc_application=send))
    monkeypatch.setattr(checker, 'GovUkNotify', factory)
    return SimpleNamespace(factory=factory, send=send, calls=calls)


@pytest.mark.parametrize('locale', ['en', 'cy'])
@pytest.mark.parametrize('changed', [False, True])
@pytest.mark.parametrize('overseas', [False, True])
@pytest.mark.parametrize('relationship,remain,died,ended,required', RELATIONSHIP_CASES)
def test_completed_checker_document_matrix(
        client, seed_checker_state, locale, changed, overseas, relationship, remain, died, ended, required):
    """CK01: eight relationship rows x name x overseas x locale = 64 renders."""
    answers = _answers(relationship, remain, died, ended, changed, overseas)
    seed_checker_state(answers, locale)
    main = _main(_page(client.get(PATHS['results'])))
    _assert_summaries(main, locale, required, changed, overseas)
    _assert_certificate(main, locale)
    assert _saved_answers(client) == answers


@pytest.mark.parametrize('locale', ['en', 'cy'])
@pytest.mark.parametrize('method', ['GET', 'POST'])
@pytest.mark.parametrize('endpoint', ['results', 'email'])
@pytest.mark.parametrize('answers,next_question', [
    pytest.param({}, 'name', id='no-answers'),
    pytest.param({FIELDS['name']: False}, 'relationship', id='name-only'),
    pytest.param(_answers(Partnership.MARRIED, overseas=None), 'remain', id='married-remain'),
    pytest.param(_answers(Partnership.CIVIL_PARTNERSHIP, overseas=None), 'remain', id='civil-remain'),
    pytest.param(_answers(died=None, ended=None, overseas=None), 'died', id='neither-death'),
    pytest.param(_answers(ended=None, overseas=None), 'ended', id='neither-ended'),
    pytest.param(_answers(Partnership.MARRIED, False, overseas=None), 'overseas', id='married-overseas'),
    pytest.param(_answers(Partnership.CIVIL_PARTNERSHIP, False, overseas=None),
                 'overseas', id='civil-overseas'),
    pytest.param(_answers(overseas=None), 'overseas', id='neither-overseas'),
])
def test_incomplete_answers_redirect_in_order(
        client, seed_checker_state, locale, method, endpoint, answers, next_question):
    """CK02: nine prefixes x two endpoints x GET/POST x locale = 72 guards."""
    seed_checker_state(answers, locale)
    before = _saved_session(client)
    response = client.open(PATHS[endpoint], method=method, data={'email_address': EMAIL})
    assert response.status_code == 302
    assert response.headers['Location'] == PATHS[next_question]
    assert _saved_session(client) == before


@pytest.mark.parametrize('locale', ['en', 'cy'])
@pytest.mark.parametrize('answer', [False, True])
@pytest.mark.parametrize('relationship', list(Partnership))
def test_questionnaire_post_progression(client, seed_checker_state, locale, answer, relationship):
    """CK03: real field names, Boolean strings and all three enum values."""
    seed_checker_state({}, locale)
    partnered = relationship is not Partnership.NEITHER
    steps = [('name', answer, 'relationship'),
             ('relationship', relationship, 'remain' if partnered else 'died')]
    steps += ([('remain', answer, 'overseas')] if partnered else
              [('died', answer, 'ended'), ('ended', answer, 'overseas')])
    steps.append(('overseas', answer, 'results'))
    for question, value, next_question in steps:
        field = FIELDS[question]
        main = _main(_page(client.get(PATHS[question])))
        offered = {node.get('value') for node in main.iter('input') if node.get('name') == field}
        assert offered == ({'MARRIED', 'CIVIL_PARTNERSHIP', 'NEITHER'}
                           if question == 'relationship' else {'True', 'False'})
        before = _saved_session(client)
        for invalid in (None, 'not-a-choice'):
            response = client.post(PATHS[question], data={} if invalid is None else {field: invalid})
            main = _main(_page(response))
            errors = _one(_elements(main, 'div', 'govuk-error-summary'))
            assert errors.findall(f".//a[@href='#{field}']")
            assert 'Location' not in response.headers
            assert _saved_session(client) == before
        posted = value.value if question == 'relationship' else str(value)
        response = client.post(PATHS[question], data={field: posted})
        assert response.status_code == 302
        assert response.headers['Location'] == PATHS[next_question]
        assert _saved_answers(client)[field] is value
        main = _main(_page(client.get(PATHS[question])))
        selected = [node.get('value') for node in main.iter('input')
                    if node.get('name') == field and 'checked' in node.attrib]
        assert selected == [posted]
    _page(client.get(PATHS['results']))


@pytest.mark.parametrize('locale', ['en', 'cy'])
def test_changed_relationship_ignores_stale_answers(client, seed_checker_state, locale):
    """CK04: normal edits retain but ignore answers from the previous branch."""
    answers = _answers(remain=True, died=True, ended=True)
    seed_checker_state(answers, locale)
    transitions = [
        ('relationship', Partnership.MARRIED, 'remain',
         MARRIED | {'partners_statutory_declaration', 'spouses_statutory_declaration'}),
        ('remain', False, 'overseas', MARRIED),
        ('relationship', Partnership.CIVIL_PARTNERSHIP, 'remain', CIVIL),
        ('remain', True, 'overseas',
         CIVIL | {'partners_statutory_declaration', 'civil_partners_statutory_declaration'}),
        ('relationship', Partnership.NEITHER, 'died', SINGLE | {'death_certificate', 'decree_absolute'}),
        ('died', False, 'ended', SINGLE | {'decree_absolute'}),
        ('ended', False, 'overseas', SINGLE),
    ]
    for question, value, next_question, required in transitions:
        field = FIELDS[question]
        posted = value.value if question == 'relationship' else str(value)
        response = client.post(PATHS[question], data={field: posted})
        assert response.status_code == 302
        assert response.headers['Location'] == PATHS[next_question]
        answers[field] = value
        assert _saved_answers(client) == answers
        main = _main(_page(client.get(PATHS['results'])))
        _assert_summaries(main, locale, required)


@pytest.mark.parametrize('relationship', list(Partnership))
def test_back_links_and_language_round_trip(client, seed_checker_state, relationship):
    """CK05: real language links/referrer redirects preserve all six answers."""
    seed_checker_state(_answers(relationship, False, False, False))
    original = _saved_session(client)[STATE_KEY]
    partnered = relationship is not Partnership.NEITHER
    back_links = {'name': 'start', 'relationship': 'name',
                  'overseas': 'remain' if partnered else 'ended',
                  'results': 'overseas', 'email': 'results', 'sent': 'results'}
    back_links.update({'remain': 'relationship'} if partnered else
                      {'died': 'relationship', 'ended': 'died'})
    results_url = ORIGIN + PATHS['results'] + '?source=language-check'
    for locale in ('en', 'cy', 'en'):
        if _saved_session(client)['lang_code'] != locale:
            page = _page(client.get(results_url))
            toggle = _one(page.findall(f".//a[@hreflang='{locale}']"))
            assert toggle.get('href') == '/set_language/' + locale
            response = client.get(toggle.get('href'), headers={'Referer': results_url})
            assert response.status_code == 302
            assert response.headers['Location'] == results_url
            page = _page(client.get(response.headers['Location']))
            _assert_certificate(_main(page), locale)
        for question, destination in back_links.items():
            page = _page(client.get(PATHS[question]))
            back = _one(_elements(page, 'a', 'govuk-back-link'))
            assert back.get('href') == PATHS[destination]
        saved = _saved_session(client)
        assert saved['lang_code'] == locale
        assert saved[STATE_KEY] == original


@pytest.mark.parametrize('locale', ['en', 'cy'])
@pytest.mark.parametrize('email,error_index', [('', 0), ('not-an-email', 1)])
def test_invalid_email_does_not_send(client, seed_checker_state, checker_notify, locale, email, error_index):
    """CK06: validation happens before Notify construction, not just before sending."""
    seed_checker_state(_answers(), locale)
    before = _saved_session(client)
    response = client.post(PATHS['email'], data={'email_address': email})
    main = _main(_page(response))
    errors = _one(_elements(main, 'div', 'govuk-error-summary'))
    error = _one(errors.findall(".//a[@href='#email_address']"))
    assert _text(error) == COPY[locale]['email_errors'][error_index]
    assert 'Location' not in response.headers
    checker_notify.factory.assert_not_called()
    checker_notify.send.assert_not_called()
    assert checker_notify.calls == []
    assert _saved_session(client) == before


@pytest.mark.parametrize('locale', ['en', 'cy'])
@pytest.mark.parametrize('changed', [False, True])
@pytest.mark.parametrize('overseas', [False, True])
@pytest.mark.parametrize('relationship,remain,died,ended,required', RELATIONSHIP_CASES)
def test_valid_email_sends_exact_checker_contract(
        client, seed_checker_state, checker_notify, locale, changed, overseas,
        relationship, remain, died, ended, required):
    """CK07: hand off exactly the existing 16 Booleans, never certificate/identity/EX160 flags."""
    seed_checker_state(_answers(relationship, remain, died, ended, changed, overseas), locale)
    before = _saved_session(client)
    response = client.post(PATHS['email'], data={'email_address': EMAIL})
    expected = _expected_flags(required, changed, overseas)
    assert len(expected) == 16
    assert response.status_code == 302
    assert response.headers['Location'] == PATHS['sent']
    checker_notify.factory.assert_called_once_with()
    checker_notify.send.assert_called_once_with(email_address=EMAIL, documents_required=expected)
    assert checker_notify.calls == [(locale, locale, EMAIL, expected)]
    actual = checker_notify.calls[0][3]
    assert len(actual) == 16
    assert all(type(value) is bool for value in actual.values())
    assert _saved_session(client) == before
    _page(client.get(response.headers['Location']))


@pytest.mark.parametrize('locale', ['en', 'cy'])
@pytest.mark.parametrize('endpoint', ['results', 'email'])
def test_checker_has_no_application_dependency(client, seed_checker_state, locale, endpoint):
    """CK08: application-store calls and SQL connections are fail-if-called."""
    seed_checker_state(_answers(), locale)
    _page(client.get(PATHS[endpoint]))
    assert set(_saved_session(client)) == {STATE_KEY, 'lang_code'}


@pytest.mark.parametrize('locale', ['en', 'cy'])
def test_helper_language_and_links(app, locale):
    """CK09: approved localized C3/C7, with unchanged certificate-order helper."""
    if locale == 'cy':
        catalogue_path = Path(app.root_path) / 'translations/cy/LC_MESSAGES/messages.po'
        with catalogue_path.open(encoding='utf-8') as source:
            approved = read_po(source, locale='cy')[POSTAL_FALLBACK]
        assert approved is not None
        assert approved.string == COPY['cy']['postal_fallback']
        assert not approved.fuzzy
    with app.test_request_context(base_url=ORIGIN):
        session['lang_code'] = locale
        assert app.preprocess_request() is None
        assert g.lang_code == locale
        certify = _HTML(str(DocumentCheckerConstants.get_birth_cert_copy_link())).root
        order = _HTML(str(DocumentCheckerConstants.get_birth_cert_uk_link())).root
    assert _text(certify) == COPY[locale]['source_quality']
    assert _text(order) == COPY[locale]['order']
    link = _one(list(certify.iter('a')))
    assert _text(link) == COPY[locale]['certify_link']
    assert link.attrib == {'href': CERTIFY_URL, 'rel': 'external', 'target': '_blank', 'class': 'govuk-link'}
    link = _one(list(order.iter('a')))
    assert _text(link) == COPY[locale]['order_link']
    assert link.attrib == {'href': ORDER_URL, 'target': '_blank', 'class': 'govuk-link'}


@pytest.mark.parametrize('locale', ['en', 'cy'])
def test_email_route_api_shaped_failure(client, seed_checker_state, checker_notify, locale):
    """CK10: narrow legacy-handler characterization, NOT the real sender HTTPError/abort chain."""
    seed_checker_state(_answers(), locale)
    before = _saved_session(client)
    message = 'Synthetic checker send rejected'
    api_response = SimpleNamespace(json=lambda: {'errors': [{'message': message}]})
    checker_notify.send.side_effect = RuntimeError(api_response)
    response = client.post(PATHS['email'], data={'email_address': EMAIL})
    main = _main(_page(response))
    errors = _one(_elements(main, 'div', 'govuk-error-summary'))
    assert message in _text(errors)
    assert 'Location' not in response.headers
    checker_notify.factory.assert_called_once_with()
    checker_notify.send.assert_called_once_with(
        email_address=EMAIL, documents_required=_expected_flags(SINGLE, False, False))
    assert checker_notify.calls == []
    assert _saved_session(client) == before
