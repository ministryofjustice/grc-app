"""Isolated NT01-13 contracts, not managed Notify rendering or delivery proof.

The runner must supply cold synthetic configuration before conftest imports.
These fixtures never request the inherited application, database or cache fixtures.
"""

from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import re
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from flask import Flask, g, render_template, session
from notifications_python_client.errors import HTTPError
from requests import Response
from werkzeug.exceptions import HTTPException

import grc.external_services.gov_uk_notify as notify
import grc.submit_and_pay as submission
from grc.business_logic.data_structures.application_data import ApplicationData
from grc.business_logic.data_structures.birth_registration_data import AdoptedInTheUkEnum
from grc.business_logic.data_structures.submit_and_pay_data import HelpWithFeesType
from grc.business_logic.data_structures.uploads_data import EvidenceFile
from grc.document_checker.doc_checker_state import CurrentlyInAPartnershipEnum, DocCheckerState
from grc.external_services.gov_uk_notify_templates import GovUkNotifyTemplateManager
from grc.list_status import ListStatus


ROOT = Path(__file__).resolve().parents[3]
RECIPIENT = 'applicant@example.invalid'
OVERRIDE = 'capture@example.invalid'
SYNTHETIC_KEY = 'not-a-real-notify-key'
FRAGMENTS = {'en': 'documents.html', 'cy': 'documents-cy.html'}
COMMON_FIELD = 'environment_and_email_address'
CERTIFY_URL = 'https://www.gov.uk/certifying-a-document'
ORDER_URL = 'https://www.gov.uk/order-copy-birth-death-marriage-certificate'
SCOTLAND_URL = 'http://www.nrscotland.gov.uk/registration/how-to-order-an-official-extract-from-the-registers'
NORTHERN_IRELAND_URL = (
    'http://www.nidirect.gov.uk/index/do-it-online/government-citizens-and-rights-online/'
    'order-a-birth-adoption-death-marriage-or-civil-partnership-certificate.htm'
)
EX160_URL = 'https://www.gov.uk/government/publications/apply-for-help-with-court-and-tribunal-fees'

BULLETS = {
    'en': {
        'birth': f'* your original or a certified copy ({CERTIFY_URL}) of your full birth certificate',
        'adoption': f'* your original or a certified copy ({CERTIFY_URL}) of your full adoption certificate',
        'official': '* an official confirmation of date of birth and birth gender',
        'ex160': f'* an EX160 form ({EX160_URL})',
    },
    'cy': {
        'birth': f"* eich gwreiddiol neu ardystiedig o'ch ({CERTIFY_URL}) tystysgrif geni llawn",
        'adoption': f"* eich gwreiddiol neu ardystiedig o'ch ({CERTIFY_URL}) tystysgrif fabwysiadu llawn",
        'official': '* cadarnhad swyddogol o\u2019ch dyddiad geni a\u2019ch rhywedd pan gawsoch eich geni',
        'ex160': f'* ffurflen EX160 ({EX160_URL})',
    },
}

# Current source IDs are frozen: no candidate clones or selector changes are approved.
# These public template identifiers are UUIDs, not authentication credentials.
ADMIN_IDS = {
    'ADMIN_LOGIN_SECURITY_CODE_TEMPLATE': str(UUID('fde1def2-bf10-45d2-8c38-2837a0a79399')),
    'ADMIN_FORGET_PASSWORD_TEMPLATE': str(UUID('fadf94d8-7d65-4eed-b52a-5f5b81aa32be')),
    'ADMIN_NEW_USER_TEMPLATE': str(UUID('0ff48a4c-601e-4cc1-b6c6-30bac012c259')),
}
TEMPLATE_IDS = {
    'en': {
        'DOCUMENTS_REQUIRED_TEMPLATE': 'a992b8c5-17e6-4dca-820c-5aa4bdd67b58',
        'APPLICATION_RECEIVED_30_WEEKS': '77007bae-b688-4dbb-bc84-334b0f5d3aef',
        'FEEDBACK_TEMPLATE': 'd83e561e-3620-47f5-983a-4b50bf3fc33c',
        'UNFINISHED_APPLICATION': '151fce32-1f66-4efd-a875-28026e8d8d70',
        'SECURITY_CODE_LOGIN': 'd93108b9-4a5b-4268-91ee-2bb59686e702',
    },
    'cy': {
        'DOCUMENTS_REQUIRED_TEMPLATE': '3bcfc20d-a2ce-4132-91fa-1fc91dd1a097',
        'APPLICATION_RECEIVED_30_WEEKS': '11aa2538-d411-42d8-8999-6d97c7b5f429',
        'FEEDBACK_TEMPLATE': '388b14cd-345b-4382-9594-b8026c2242a6',
        'UNFINISHED_APPLICATION': '6d981947-7fa7-4c62-8912-f4324cd050ee',
        'SECURITY_CODE_LOGIN': '1e5f89f3-44ea-4f08-8458-b4f1ef369e74',
    },
}
CHECKER_FLAGS = {
    'need_to_send_name_change_documents': True,
    'need_to_send_medical_reports': True,
    'need_to_send_evidence_of_living_in_gender': True,
    'need_to_send_statutory_declaration_for_single_applicant': False,
    'need_to_send_statutory_declaration_for_applicant_in_partnership': True,
    'need_to_send_partners_statutory_declaration': True,
    'need_to_send_partnership_certificate': True,
    'need_to_send_death_certificate': False,
    'need_to_send_decree_absolute': False,
    'need_to_send_proof_gender_recognised_outside_uk': False,
    'need_to_send_statutory_declaration_for_married_applicant': True,
    'need_to_send_statutory_declaration_for_applicant_in_civil_partnership': False,
    'need_to_send_spouses_statutory_declaration': True,
    'need_to_send_civil_partners_statutory_declaration': False,
    'need_to_send_marriage_certificate': True,
    'need_to_send_civil_partnership_certificate': False,
}
AGGREGATE_FLAGS = {
    'need_to_send_statutory_declaration_for_applicant_in_partnership',
    'need_to_send_partners_statutory_declaration',
    'need_to_send_partnership_certificate',
}
REFERENCE_NAMES = {
    'checker': 'Documents you need for your Gender Recognition Certificate application',
    'receipt': 'Application received - 30 weeks',
}
REFERENCE_SUBJECTS = {
    ('checker', 'en'): 'Documents you need for your Gender Recognition Certificate application',
    ('checker', 'cy'): 'Dogfennau sydd eu hangen arnoch ar gyfer eich cais am Dystysgrif Cydnabod Rhywedd',
    ('receipt', 'en'): 'Your application has been received',
    ('receipt', 'cy'): ' Mae eich cais wedi cyrraedd',
}

# Independent English draft oracle: 02-notify-design.md, N-C1/N-C2 and all N-R1-N-R8.
# These are local acceptance expectations, not managed-template or WLU approval.
CHECKER_INTRO = (
    'You can upload most documents online, including your birth or adoption certificate. '
    'You can also post your birth or adoption certificate to us if you cannot upload it.'
)
CHECKER_CERTIFICATE_BLOCK = f"""# Birth or adoption certificate

Use the original or a certified copy of your full birth or adoption certificate.

You can upload a scan or good quality photograph of your full birth or adoption certificate.

If you upload your certificate, you do not need to post it to us unless we ask you to.

If you have an adoption certificate, upload that instead of your birth certificate.

If you cannot upload your certificate, post it after you submit your application.

You can order a birth certificate if your birth was registered in the UK. See the following link for guidance about this:
{ORDER_URL}

See the following link for guidance about certifying copies of documents:
{CERTIFY_URL}"""
RECEIPT_NEXT_STEPS_BLOCK = '\n\n'.join((
    '#What you need to do next',
    'Only post documents if they are listed below. If no documents are listed, '
    'you do not need to post any documents to us unless we ask you to.',
    '((documents_to_be_posted))',
    'If any documents are listed above, post them as soon as possible. '
    'Include your name and address so we can match them to your application.',
    'If you post documents to us, they will be posted back to you.',
    'If you need to post any of the documents listed above, send them to:',
    'Gender Recognition Panel\nPO Box 11230\nLeicester\nLE1 8FQ',
    'If you need to send any of the listed documents by courier, please contact us first (details below).',
    '^ If you need to obtain a certificate listed above, you can '
    f'[order a birth, death, marriage or civil partnership certificate online]({ORDER_URL}) '
    "if you live in England and Wales. There's a different process for "
    f'[getting certificates in Scotland]({SCOTLAND_URL}) and [Northern Ireland]({NORTHERN_IRELAND_URL}).',
    'Your application will be reviewed by the Gender Recognition Panel. '
    'You will be contacted if they need more information.',
    'You will then be told if you will be issued with a Gender Recognition Certificate, '
    'and what you can do if your application has not been accepted.',
    'The panel will usually look at your application within 30 weeks of applying.',
    '^ If we need to contact you by post in the next 6 months, please let us know '
    'if there are any dates we should avoid (for example, if you are away on holiday).',
))


def unexpected_side_effect(*args, **kwargs):
    pytest.fail('Unexpected HTTP or submission artifact side effect in isolated Notify tests')


@pytest.fixture(autouse=True)
def no_http(monkeypatch):
    monkeypatch.setattr('requests.sessions.Session.request', unexpected_side_effect)


@pytest.fixture
def notify_app():
    app = Flask(__name__, template_folder=str(ROOT / 'grc' / 'templates'))
    app.config.update(
        TESTING=True,
        SECRET_KEY='synthetic-notify-test-secret',
        ENVIRONMENT='test',
        FLASK_APP='grc',
        NOTIFY_API=SYNTHETIC_KEY,
        NOTIFY_OVERRIDE_EMAIL=None,
    )
    return app


@pytest.fixture(params=['en', 'cy'])
def language(request):
    return request.param


@contextmanager
def notify_context(app, language):
    with app.test_request_context('/', base_url='https://notify-tests.invalid/'):
        session['lang_code'] = language
        g.lang_code = language
        yield


@pytest.fixture
def sdk_fake(monkeypatch):
    captured = SimpleNamespace(keys=[], calls=[], response={'id': 'synthetic-notification'}, error=None)

    class FakeClient:
        def __init__(self, api_key):
            assert api_key == SYNTHETIC_KEY
            captured.keys.append(api_key)

        def send_email_notification(self, *, email_address, template_id, personalisation):
            assert email_address.endswith('@example.invalid')
            captured.calls.append(deepcopy({
                'email_address': email_address,
                'template_id': template_id,
                'personalisation': personalisation,
            }))
            if captured.error is not None:
                raise captured.error
            return captured.response

    monkeypatch.setattr(notify, 'NotificationsAPIClient', FakeClient)
    return captured


def certificate_file(key, password_required=False):
    evidence = EvidenceFile()
    evidence.original_file_name = 'certificate.pdf'
    evidence.aws_file_name = f'NTFY0001__birthOrAdoptionCertificate__{key}.pdf'
    evidence.password_required = password_required
    return evidence


def nonblank_lines(fragment):
    return [line.strip() for line in fragment.splitlines() if line.strip()]


def read_reference(kind, language):
    name = REFERENCE_NAMES[kind] + (' - Welsh' if language == 'cy' else '')
    text = (ROOT / 'Gov.UK Notify templates' / f'{name}.txt').read_text(encoding='utf-8')
    envelope = {}
    for tag in ('templateId', 'TemplateName', 'From', 'To', 'Subject', 'Message'):
        matches = re.findall(rf'^<{tag}>\n(.*?)\n</{tag}>$', text, re.MULTILINE | re.DOTALL)
        assert len(matches) == 1, (name, tag)
        envelope[tag] = matches[0]  # Preserve subject whitespace; this is not XML or a Notify renderer.
    return envelope


@pytest.mark.parametrize('using_ex160', [False, True], ids=['no-ex160', 'ex160'])
@pytest.mark.parametrize('files,remove_one,status,needs_certificate', [
    pytest.param((), False, ListStatus.NOT_STARTED, True, id='empty'),
    pytest.param((('a', False),), False, ListStatus.COMPLETED, False, id='one-valid'),
    pytest.param((('a', False), ('b', False)), False, ListStatus.COMPLETED, False, id='multiple-valid'),
    pytest.param((('a', True),), False, ListStatus.ERROR, True, id='protected'),
    pytest.param((('a', False), ('b', True)), False, ListStatus.ERROR, True, id='mixed-valid-protected'),
    pytest.param((('a', False), ('a', False)), False, ListStatus.ERROR, True, id='duplicate-keys'),
    pytest.param((('a', False), ('b', False)), True, ListStatus.COMPLETED, False, id='remove-one'),
    pytest.param((('a', False),), True, ListStatus.NOT_STARTED, True, id='remove-last'),
])
def test_receipt_fragment_state_matrix(notify_app, language, using_ex160, files, remove_one, status, needs_certificate):
    application = ApplicationData()
    application.birth_registration_data.birth_registered_in_uk = True
    application.birth_registration_data.adopted = False
    application.uploads_data.birth_or_adoption_certificates = [certificate_file(*entry) for entry in files]
    application.submit_and_pay_data.how_applying_for_help_with_fees = (
        HelpWithFeesType.USING_EX160_FORM if using_ex160 else None
    )
    if remove_one:
        assert application.section_status_birth_or_adoption_certificates is ListStatus.COMPLETED
        assert application.needs_to_post_birth_or_adoption_certificate is False
        application.uploads_data.birth_or_adoption_certificates.pop()

    with notify_context(notify_app, language):
        fragment = render_template(FRAGMENTS[language], application_data=application)

    expected = [BULLETS[language]['birth']] if needs_certificate else []
    if using_ex160:
        expected.append(BULLETS[language]['ex160'])
    assert nonblank_lines(fragment) == expected
    assert application.section_status_birth_or_adoption_certificates is status
    assert application.has_usable_birth_or_adoption_certificate is (not needs_certificate)
    assert application.needs_to_post_birth_or_adoption_certificate is needs_certificate
    assert application.needs_to_post_documents is (needs_certificate or using_ex160)


@pytest.mark.parametrize('registered_in_uk,adopted,adoption_location,bullet', [
    pytest.param(True, False, None, 'birth', id='uk-birth'),
    pytest.param(True, True, AdoptedInTheUkEnum.ADOPTED_IN_THE_UK_YES, 'adoption', id='uk-adoption'),
    pytest.param(True, True, AdoptedInTheUkEnum.ADOPTED_IN_THE_UK_NO, 'adoption', id='adopted-outside-uk'),
    pytest.param(True, True, AdoptedInTheUkEnum.ADOPTED_IN_THE_UK_DO_NOT_KNOW, 'adoption', id='adoption-unknown'),
    pytest.param(False, False, None, 'official', id='non-uk-birth'),
    pytest.param(False, True, AdoptedInTheUkEnum.ADOPTED_IN_THE_UK_YES, 'official', id='non-uk-adopted'),
])
def test_receipt_registration_and_adoption_wording(notify_app, language, registered_in_uk, adopted, adoption_location, bullet):
    application = ApplicationData()
    application.birth_registration_data.birth_registered_in_uk = registered_in_uk
    application.birth_registration_data.adopted = adopted
    application.birth_registration_data.adopted_in_the_uk = adoption_location
    application.submit_and_pay_data.how_applying_for_help_with_fees = HelpWithFeesType.USING_ONLINE_SERVICE

    with notify_context(notify_app, language):
        for recognised_overseas in (False, True):
            application.confirmation_data.gender_recognition_outside_uk = recognised_overseas
            application.confirmation_data.gender_recognition_from_approved_country = True
            fragment = render_template(FRAGMENTS[language], application_data=application)
            assert nonblank_lines(fragment) == [BULLETS[language][bullet]]
            assert application.submit_and_pay_data.is_using_ex160_form is False


def test_empty_fragment_is_not_a_postal_boolean(notify_app, language):
    application = ApplicationData()
    application.uploads_data.birth_or_adoption_certificates = [certificate_file('a')]
    with notify_context(notify_app, language):
        fragment = render_template(FRAGMENTS[language], application_data=application)
    assert fragment.strip() == ''
    assert application.needs_to_post_documents is False


@pytest.mark.parametrize('app_id,lang_code,expected_language', [
    ('grc', 'en', 'en'),
    ('grc', 'cy', 'cy'),
    ('admin', 'cy', 'en'),
    (None, 'cy', 'en'),
])
def test_template_selection_is_locale_and_application_scoped(notify_app, app_id, lang_code, expected_language):
    # NT04/NT11: a Welsh instance must not mutate class defaults or unrelated selectors.
    with notify_context(notify_app, 'cy'):
        previous_welsh = GovUkNotifyTemplateManager('grc')
    with notify_context(notify_app, lang_code):
        manager = GovUkNotifyTemplateManager(app_id)
    expected = {**ADMIN_IDS, **TEMPLATE_IDS[expected_language]}
    assert {key: getattr(manager, key) for key in expected} == expected
    assert {key: getattr(previous_welsh, key) for key in TEMPLATE_IDS['cy']} == TEMPLATE_IDS['cy']
    assert {key: getattr(GovUkNotifyTemplateManager, key) for key in TEMPLATE_IDS['en']} == TEMPLATE_IDS['en']


@pytest.mark.parametrize('fragment_kind', ['empty', 'whitespace', 'ex160', 'fallback'])
def test_completed_application_sender_preserves_fragment(notify_app, sdk_fake, language, fragment_kind):
    fragment = {
        'empty': '',
        'whitespace': '\n   \n',
        'ex160': f"\n{BULLETS[language]['ex160']}\n",
        'fallback': f"\n  {BULLETS[language]['birth']}\n",
    }[fragment_kind]
    with notify_context(notify_app, language):
        response = notify.GovUkNotify().send_email_completed_application(RECIPIENT, fragment)
    assert response is sdk_fake.response
    assert sdk_fake.keys == [SYNTHETIC_KEY]
    assert sdk_fake.calls == [{
        'email_address': RECIPIENT,
        'template_id': TEMPLATE_IDS[language]['APPLICATION_RECEIVED_30_WEEKS'],
        'personalisation': {'documents_to_be_posted': fragment, COMMON_FIELD: f'[test to:{RECIPIENT}] '},
    }]


def test_checker_sender_preserves_boolean_contract(notify_app, sdk_fake, language):
    state = DocCheckerState()
    state.changed_name_to_reflect_gender = True
    state.currently_in_a_partnership = CurrentlyInAPartnershipEnum.MARRIED
    state.plan_to_remain_in_a_partnership = True
    state.previous_partnership_partner_died = False
    state.previous_partnership_ended = False
    state.gender_recognition_outside_uk = False
    payload = state.get_list_of_documents_required_values()
    assert payload == CHECKER_FLAGS
    assert len(payload) == 16
    assert all(type(value) is bool for value in payload.values())

    with notify_context(notify_app, language):
        response = notify.GovUkNotify().send_email_documents_you_need_for_your_grc_application(RECIPIENT, payload)
    assert response is sdk_fake.response
    assert sdk_fake.calls == [{
        'email_address': RECIPIENT,
        'template_id': TEMPLATE_IDS[language]['DOCUMENTS_REQUIRED_TEMPLATE'],
        'personalisation': {**CHECKER_FLAGS, COMMON_FIELD: f'[test to:{RECIPIENT}] '},
    }]
    sent = sdk_fake.calls[0]['personalisation']
    assert all(type(sent[key]) is bool for key in CHECKER_FLAGS)
    assert state.get_list_of_documents_required_values() == CHECKER_FLAGS


@pytest.mark.parametrize('override', [None, OVERRIDE], ids=['no-override', 'override'])
@pytest.mark.parametrize('environment,prefix_space', [
    ('production', None), ('test', 'test'), ('Production', 'Production'), (None, 'local'),
], ids=['production', 'test', 'case-sensitive', 'default-local'])
def test_environment_and_recipient_routing(notify_app, sdk_fake, environment, prefix_space, override):
    if environment is None:
        notify_app.config.pop('ENVIRONMENT')
    else:
        notify_app.config['ENVIRONMENT'] = environment
    notify_app.config['NOTIFY_OVERRIDE_EMAIL'] = override
    original = {'documents_to_be_posted': '\n'}
    template_id = TEMPLATE_IDS['en']['APPLICATION_RECEIVED_30_WEEKS']
    with notify_context(notify_app, 'en'):
        response = notify.GovUkNotify().send_email(RECIPIENT, template_id, original)
    expected_recipient = RECIPIENT if prefix_space is None or override is None else override
    expected_prefix = '' if prefix_space is None else f'[{prefix_space} to:{RECIPIENT}] '
    assert response is sdk_fake.response
    assert sdk_fake.calls == [{
        'email_address': expected_recipient,
        'template_id': template_id,
        'personalisation': {'documents_to_be_posted': '\n', COMMON_FIELD: expected_prefix},
    }]
    assert original == {'documents_to_be_posted': '\n', COMMON_FIELD: expected_prefix}


def test_send_mutates_only_common_personalisation_field(notify_app, sdk_fake):
    payload = {'documents_to_be_posted': '\n', 'untouched': ['synthetic'], COMMON_FIELD: 'caller prefix'}
    before = deepcopy(payload)
    other_recipient = 'second@example.invalid'
    template_id = TEMPLATE_IDS['en']['APPLICATION_RECEIVED_30_WEEKS']
    with notify_context(notify_app, 'en'):
        sender = notify.GovUkNotify()
        sender.send_email(RECIPIENT, template_id, payload)
        assert payload == {**before, COMMON_FIELD: f'[test to:{RECIPIENT}] '}
        sender.send_email(other_recipient, template_id, payload)
    assert payload == {**before, COMMON_FIELD: f'[test to:{other_recipient}] '}
    assert [call['personalisation'] for call in sdk_fake.calls] == [
        {**before, COMMON_FIELD: f'[test to:{RECIPIENT}] '},
        {**before, COMMON_FIELD: f'[test to:{other_recipient}] '},
    ]
    assert sdk_fake.keys == [SYNTHETIC_KEY]


@pytest.mark.parametrize('status_code', [400, 503])
def test_notify_http_error_becomes_http_exception(notify_app, sdk_fake, status_code):
    response = Response()
    response.status_code = status_code
    response._content = b'{"errors": [{"error": "BadRequestError", "message": "Synthetic Notify failure"}]}'
    sdk_fake.error = HTTPError(response)
    with notify_context(notify_app, 'en'):
        with pytest.raises(HTTPException) as raised:
            notify.GovUkNotify().send_email_completed_application(RECIPIENT, '')
    assert raised.value.code == status_code
    assert sdk_fake.keys == [SYNTHETIC_KEY]
    assert len(sdk_fake.calls) == 1


@pytest.mark.parametrize('kind', ['checker', 'receipt'])
def test_reference_envelopes_and_placeholders_match_contract(kind, language):
    envelope = read_reference(kind, language)
    selector = 'DOCUMENTS_REQUIRED_TEMPLATE' if kind == 'checker' else 'APPLICATION_RECEIVED_30_WEEKS'
    assert envelope['templateId'] == TEMPLATE_IDS[language][selector]
    assert envelope['TemplateName'] == REFERENCE_NAMES[kind] + (' - Welsh' if language == 'cy' else '')
    assert envelope['From'] == 'Gender Recognition Certificate'
    assert envelope['To'] == 'email address'
    assert envelope['Subject'] == f'(({COMMON_FIELD}))' + REFERENCE_SUBJECTS[kind, language]
    placeholders = Counter(re.findall(r'\(\(([a-z_]+)(?:\?\?|\)\))', envelope['Message']))
    if kind == 'checker':
        assert placeholders == Counter({key: 2 for key in CHECKER_FLAGS if key not in AGGREGATE_FLAGS})
        assert Counter(re.findall(r'\(\(([a-z_]+)\?\?', envelope['Message'])) == placeholders
        expected_urls = {
            CERTIFY_URL, ORDER_URL, 'https://www.gov.uk/apply-gender-recognition-certificate',
            'https://www.gov.uk/copy-decree-absolute-final-order',
            'https://www.gov.uk/government/publications/gender-recognition-certificate-list-of-approved-countries-and-territories',
            'https://www.gov.uk/government/publications/gender-recognition-certificate-statutory-declarations-for-applicants',
            'https://www.gov.uk/government/publications/gender-recognition-certificate-writing-medical-reports',
            'https://www.gov.uk/government/publications/gender-recognition-certificate-list-of-medical-practitioners-in-gender-dysphoria',
        }
    else:
        assert placeholders == Counter({'documents_to_be_posted': 1})
        assert envelope['Message'].count('((documents_to_be_posted))') == 1
        expected_urls = {ORDER_URL, SCOTLAND_URL, NORTHERN_IRELAND_URL}
        assert 'Gender Recognition Panel\nPO Box 11230\nLeicester\nLE1 8FQ' in envelope['Message']
        assert 'GRPenquiries@justice.gov.uk' in envelope['Message']
        assert '0300 303 5857' in envelope['Message']
    assert set(re.findall(r'https?://[^\s<>()]+', envelope['Message'])) == expected_urls


@pytest.mark.parametrize('kind', ['checker', 'receipt'])
def test_reference_guidance_matches_approved_english_draft(kind):
    body = read_reference(kind, 'en')['Message']
    if kind == 'checker':
        introduction = body.split('((need_to_send_name_change_documents??', 1)[0]
        assert CHECKER_INTRO in introduction
        assert 'Some documents will be uploaded during the application process' not in introduction
        start = body.index('# Birth or adoption certificate')
        end = body.index('# If any of your documents are not in English', start)
        assert body[start:end].strip() == CHECKER_CERTIFICATE_BLOCK
        assert 'Send an original or certified copy' not in body[start:end]
        assert body.count('# Birth or adoption certificate') == 1
        assert 'You\u2019ll need to send in both the original documents and the translations.' in body[end:]
    else:
        start = body.index('#What you need to do next')
        end = body.index('#If you need to contact us', start)
        assert body[start:end].strip() == RECEIPT_NEXT_STEPS_BLOCK
        assert 'Post the rest of your documents' not in body[start:end]
        assert '\nYou need to post:\n' not in body[start:end]
        assert body.startswith('Your application for a Gender Recognition Certificate has been received.\n')
        for preserved in (
            'Include your application reference number \u2013 we will post this when we have received your application.',
            'If you need to contact us before this, include your full name and postcode.',
            'GRPenquiries@justice.gov.uk', 'Telephone: 0300 303 5857',
            'Monday to Friday, 9am to 5pm', 'Find out about call charges',
        ):
            assert preserved in body[end:]


def test_welsh_checker_reference_guidance_matches_approved_copy():
    # Independent literals: attachment 790571, TPET-919 comment 2177487, 6 October.
    # Preserve approved internal double spaces (rows 3 and 13), not just meaning.
    body = read_reference('checker', 'cy')['Message']
    introduction = body.split('((need_to_send_name_change_documents??', 1)[0]
    assert introduction.split('\n\n')[-2] == (
        "Gallwch uwchlwytho'r rhan fwyaf o ddogfennau ar-lein, gan gynnwys eich tystysgrif geni neu fabwysiadu. "
        "Gallwch hefyd bostio'ch tystysgrif geni neu  fabwysiadu atom os na allwch ei huwchlwytho."
    )
    start = body.index('# Tystysgrif geni neu fabwysiadu')
    end = body.index("# Os nad yw unrhyw un o'ch dogfennau yn Saesneg", start)
    assert body[start:end].strip() == """# Tystysgrif geni neu fabwysiadu

Defnyddiwch gopi gwreiddiol neu ardystiedig o'ch tystysgrif geni neu fabwysiadu llawn.

Gallwch uwchlwytho sgan neu lun o ansawdd da o'ch tystysgrif geni neu fabwysiadu lawn.

Os byddwch yn uwchlwytho eich tystysgrif, nid oes angen i chi ei phostio atom oni bai ein bod yn gofyn i chi wneud hynny.

Os oes gennych dystysgrif mabwysiadu, uwchlwythwch honno yn lle eich tystysgrif geni.

Os na allwch uwchlwytho eich tystysgrif, postiwch hi ar ôl cyflwyno eich cais.

Gallwch archebu tystysgrif geni os cofrestrwyd eich genedigaeth yn y DU.

Cliciwch ar y ddolen ganlynol i gael cyfarwyddyd am hyn:
https://www.gov.uk/order-copy-birth-death-marriage-certificate

Cliciwch ar y ddolen ganlynol i gael cyfarwyddyd ar ardystio copïau o ddogfennau:
https://www.gov.uk/certifying-a-document"""
    assert 'Os nad ydych yn gallu cadarnhau eich hunaniaeth ar-lein' not in body
    assert 'Bydd gofyn i chi uwchlwytho rhai dogfennau' not in introduction
    assert body.count('# Tystysgrif geni neu fabwysiadu') == 1
    assert "Bydd angen i chi anfon y dogfennau gwreiddiol a'r cyfieithiadau atom." in body[end:]
    test_reference_envelopes_and_placeholders_match_contract('checker', 'cy')


def test_welsh_receipt_reference_guidance_matches_approved_copy():
    body = read_reference('receipt', 'cy')['Message']
    start = body.index('#Beth sydd angen i chi ei wneud nesaf')
    end = body.index('#Os byddwch angen cysylltu â ni', start)
    assert body[start:end].strip() == """#Beth sydd angen i chi ei wneud nesaf

Dim ond dogfennau sydd wedi'u rhestru isod y dylech eu postio. Os na restrir dogfennau, nid ydych angen postio unrhyw ddogfennau atom oni bai y byddwn yn gofyn ichi.

((documents_to_be_posted))

Os rhestrir unrhyw ddogfennau uchod, postiwch nhw gynted â phosibl. Rhowch eich enw a'ch cyfeiriad fel y gallwn eu paru â'ch cais.

Os byddwch yn postio dogfennau atom, byddant yn cael eu postio yn ôl atoch.

Os byddwch angen postio unrhyw un o'r dogfennau a restrwyd uchod, anfonwch nhw i:

Gender Recognition Panel
PO Box 11230
Leicester
LE1 8FQ

Os byddwch angen anfon unrhyw un o'r dogfennau a restrwyd drwy gludwr, cysylltwch â ni yn gyntaf (manylion isod).

^ Os byddwch angen cael tystysgrif a restrwyd uchod, gallwch [archebu tystysgrif geni, tystysgrif marwolaeth, tystysgrif priodas neu dystysgrif partneriaeth sifil ar-lein](https://www.gov.uk/order-copy-birth-death-marriage-certificate) os ydych chi’n byw yng Nghymru a Lloegr. Mae’r broses ar gyfer [cael tystysgrifau yn wahanol yn yr Alban](http://www.nrscotland.gov.uk/registration/how-to-order-an-official-extract-from-the-registers) a [Gogledd Iwerddon](http://www.nidirect.gov.uk/index/do-it-online/government-citizens-and-rights-online/order-a-birth-adoption-death-marriage-or-civil-partnership-certificate.htm).

Bydd eich cais yn cael ei adolygu gan y Panel Cydnabod Rhywedd.  Byddant yn cysylltu â chi os byddant angen mwy o wybodaeth.

Yna fe ddywedir wrthych os byddwch yn cael Tystysgrif Cydnabod Rhywedd, a beth allwch wneud os nad yw eich cais yn llwyddiannus.

Gan amlaf bydd y panel yn adolygu eich cais o fewn 30 wythnos i chi wneud cais.

^ Os bydd angen i ni gysylltu â chi drwy’r post yn y 6 mis nesaf, rhowch wybod i ni os oes yna unrhyw ddyddiadau y dylem osgoi (er enghraifft, os byddwch i ffwrdd ar wyliau)."""
    assert 'Postiwch weddill eich dogfennau' not in body[start:end]
    assert '\nMae angen i chi bostio:\n' not in body[start:end]
    assert body.startswith('Mae eich cais am Dystysgrif Cydnabod Rhywedd wedi cyrraedd.\n')
    assert body[end:] == """#Os byddwch angen cysylltu â ni

Bydd angen i chi gynnwys cyfeirnod eich cais - byddwn yn postio hwn atoch pan fyddwn wedi cael eich cais.

Os byddwch angen cysylltu â ni cyn hyn, dylech gynnwys eich enw llawn a’ch cod post.

GRPenquiries@justice.gov.uk
Rhif ffôn: 0300 303 5857
Dydd Llun i ddydd Gwener, 9am i 5pm
Gwybodaeth am gost galwadau"""
    test_reference_envelopes_and_placeholders_match_contract('receipt', 'cy')


def test_submission_selects_matching_fragment_and_recipient(notify_app, sdk_fake, monkeypatch, language):
    application = ApplicationData()
    application.reference_number = 'NTFY0001'
    application.email_address = RECIPIENT
    application.personal_details_data.contact_email_address = 'contact@example.invalid'
    application.birth_registration_data.birth_registered_in_uk = True
    application.birth_registration_data.adopted = True
    application.submit_and_pay_data.how_applying_for_help_with_fees = HelpWithFeesType.USING_EX160_FORM

    mark_complete = Mock()
    anonymise = Mock()
    thread = Mock(spec=['start'])
    thread_factory = Mock(return_value=thread)
    query = Mock(spec=['filter'])
    query.filter.return_value = ()
    # Keep column expressions real, but never access the model's database-backed query.
    model = submission.Application
    monkeypatch.setattr(submission, 'Application', SimpleNamespace(
        status=model.status, email=model.email, reference_number=model.reference_number, query=query,
    ))
    monkeypatch.setattr(submission, 'mark_complete', mark_complete)
    monkeypatch.setattr(submission, 'anonymise_application', anonymise)
    monkeypatch.setattr(submission, 'threading', SimpleNamespace(Thread=thread_factory))
    monkeypatch.setattr(submission, 'ApplicationFiles', unexpected_side_effect)
    monkeypatch.setattr(submission, 'mark_files_created', unexpected_side_effect)

    with notify_context(notify_app, language):
        submission.handle_successful_submission(application)

    mark_complete.assert_called_once_with('NTFY0001')
    thread_factory.assert_called_once()
    assert callable(thread_factory.call_args.kwargs['target'])
    assert thread_factory.call_args.kwargs['args'] == ['NTFY0001', application]
    thread.start.assert_called_once_with()
    query.filter.assert_called_once()
    anonymise.assert_not_called()
    assert sdk_fake.keys == [SYNTHETIC_KEY]
    assert len(sdk_fake.calls) == 1
    call = sdk_fake.calls[0]
    assert call['email_address'] == RECIPIENT
    assert call['email_address'] != application.personal_details_data.contact_email_address
    assert call['template_id'] == TEMPLATE_IDS[language]['APPLICATION_RECEIVED_30_WEEKS']
    assert set(call['personalisation']) == {'documents_to_be_posted', COMMON_FIELD}
    assert call['personalisation'][COMMON_FIELD] == f'[test to:{RECIPIENT}] '
    assert nonblank_lines(call['personalisation']['documents_to_be_posted']) == [
        BULLETS[language]['adoption'], BULLETS[language]['ex160'],
    ]
