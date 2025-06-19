import pytest
from unittest.mock import patch, MagicMock
from time import time

@pytest.fixture(autouse = True)
def clear_cache(did_doc_cache):
    # Clear the cache before each test
    did_doc_cache._cache.clear()
    did_doc_cache._expiry.clear()
    yield

def test_get_did_document_when_in_cache(did_doc_cache, app):
    with app.test_request_context():
        did_url = "https://onelogin.gov.uk/.well-known/did.json"
        mock_did_doc = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": "did:test:123",
            "verificationMethod": [],
            "authentication": [],
            "assertionMethod": []
        }
        expected_expiry = time() + 3600

        did_doc_cache._cache[did_url] = mock_did_doc
        did_doc_cache._expiry[did_url] = expected_expiry

        with patch("grc.one_login.one_login_did_doc_cache.requests.get") as mock_get:

            result_did_document = did_doc_cache.get_did_document(did_url)

            assert result_did_document == mock_did_doc
            mock_get.assert_not_called()



def test_get_did_document_not_in_cache(did_doc_cache, app):
    with app.test_request_context():
        did_url = "https://onelogin.gov.uk/.well-known/did.json"
        mock_did_doc = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": "did:test:123",
            "verificationMethod": [],
            "authentication": [],
            "assertionMethod": []
        }

        with patch("grc.one_login.one_login_did_doc_cache.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_did_doc
            mock_response.headers = {"Cache-Control": "max-age=600"}
            mock_get.return_value = mock_response

            did_document = did_doc_cache.get_did_document(did_url)

            assert did_document == mock_did_doc
            assert did_doc_cache._cache[did_url] == mock_did_doc
            assert did_url in did_doc_cache._expiry
            mock_get.assert_called_once_with(did_url)


def test_get_did_document_expired_cache(did_doc_cache, app):
    with app.test_request_context():
        did_url = "https://onelogin.gov.uk/.well-known/did.json"
        mock_did_doc = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": "did:test:123",
            "verificationMethod": [],
            "authentication": [],
            "assertionMethod": []
        }
        did_doc_cache._cache[did_url] = mock_did_doc
        did_doc_cache._expiry[did_url] = time() - 1  # Set expiry in the past

        with patch("grc.one_login.one_login_did_doc_cache.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_did_doc
            mock_response.headers = {"Cache-Control": "max-age=600"}
            mock_get.return_value = mock_response

            result_did_document = did_doc_cache.get_did_document(did_url)

            assert result_did_document == mock_did_doc
            assert did_doc_cache._cache[did_url] == mock_did_doc
            assert did_url in did_doc_cache._expiry
            mock_get.assert_called_once_with(did_url)


def test_get_did_document_expired_cache_failed_fetch(did_doc_cache, app):
    with app.test_request_context():
        did_url = "https://onelogin.gov.uk/.well-known/did.json"
        mock_did_doc = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": "did:test:123",
            "verificationMethod": [],
            "authentication": [],
            "assertionMethod": []
        }
        did_doc_cache._cache[did_url] = mock_did_doc
        did_doc_cache._expiry[did_url] = time() - 1  # Set expiry in the past

        with patch("grc.one_login.one_login_did_doc_cache.requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")


            result_document = did_doc_cache.get_did_document(did_url)
            # Since the fetch failed, we should return the cached document

            assert result_document == mock_did_doc
            mock_get.assert_called_once_with(did_url)


def test_get_did_document_failed_fetch_no_cache(did_doc_cache, app):
    with app.test_request_context():
        did_url = "https://onelogin.gov.uk/.well-known/did.json"
        expected_error_message = "Failed to fetch and no cached DID document available: Network error"

        with patch("grc.one_login.one_login_did_doc_cache.requests.get") as mock_get:
            mock_get.side_effect = Exception(expected_error_message)

            with pytest.raises(Exception) as exc_info:
                did_doc_cache.get_did_document(did_url)

            assert expected_error_message in str(exc_info.value)
            mock_get.assert_called_once_with(did_url)


@pytest.mark.parametrize("cache_control,expected", [
    ("public, max-age=7200, must-revalidate", 7200),
    ("no-store, max-age=1800", 1800),
    ("max-age=600", 600),
    ("max-age=invalid", 3600),  # Invalid number, should return default
    ("", 3600),                 # Empty string, should return default
])
def test_parse_max_age_with_valid_header(cache_control, expected, did_doc_cache):
    assert did_doc_cache._parse_max_age(cache_control) == expected