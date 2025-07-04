import pytest
from unittest.mock import patch, MagicMock
from time import time

def test_get_did_document_uses_cache(app, cache):
    with app.app_context():
        did_url = "https://onelogin.gov.uk/.well-known/did.json"
        mock_did_doc = {"id": "did:test:123"}

        with patch("grc.one_login.one_login_did_doc_cache.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_did_doc
            mock_get.return_value = mock_response

            from grc.one_login.one_login_did_doc_cache import DIDDocumentCache
            result = DIDDocumentCache.get_did_document(did_url)
            assert result == mock_did_doc
            mock_get.assert_called_once()

        with patch("grc.one_login.one_login_did_doc_cache.requests.get") as mock_get:
            result_cached = DIDDocumentCache.get_did_document(did_url)
            assert result_cached == mock_did_doc
            mock_get.assert_not_called()

def test_get_did_document_cache_bust(app, cache):
    with app.app_context():
        did_url = "https://onelogin.gov.uk/.well-known/did.json"
        mock_did_doc = {"id": "did:test:123"}

        from grc.one_login.one_login_did_doc_cache import DIDDocumentCache

        with patch("grc.one_login.one_login_did_doc_cache.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_did_doc
            mock_get.return_value = mock_response
            DIDDocumentCache.get_did_document(did_url)

        cache.delete_memoized(DIDDocumentCache.get_did_document, did_url)

        with patch("grc.one_login.one_login_did_doc_cache.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_did_doc
            mock_get.return_value = mock_response

            result = DIDDocumentCache.get_did_document(did_url)
            assert result == mock_did_doc
            mock_get.assert_called_once()