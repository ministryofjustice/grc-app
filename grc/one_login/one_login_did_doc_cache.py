import requests
from time import time

class DIDDocumentCache:
    """
    Caches DID documents in memory to reduce repeated network calls.
    """
    _cache = {}   # Stores the cached DID documents
    _expiry = {}  # Stores the expiration timestamps for each cached document

    @staticmethod
    def get_did_document(did_url: str) -> dict:
        """
        Retrieves a DID document from cache or fetches it from the given URL.

        :param did_url: The URL of the DID document to fetch.
        :return: Parsed DID document as a dictionary.
        :raises: Exception if fetching fails and no cached document is available.
        """
        now = time()

        if did_url in DIDDocumentCache._cache and now < DIDDocumentCache._expiry.get(did_url, 0):
            return DIDDocumentCache._cache[did_url]

        try:
            response = requests.get(did_url)
            response.raise_for_status()
            did_document = response.json()

            cache_control = response.headers.get('Cache-Control', '')
            max_age = DIDDocumentCache._parse_max_age(cache_control)

            DIDDocumentCache._cache[did_url] = did_document
            DIDDocumentCache._expiry[did_url] = now + max_age
            return did_document

        except Exception as e:
            if did_url in DIDDocumentCache._cache:
                return DIDDocumentCache._cache[did_url]
            raise Exception(f"Failed to fetch and no cached DID document available: {str(e)}")

    @staticmethod
    def _parse_max_age(cache_control: str) -> int:
        """
        Parses the Cache-Control header to extract max-age value.

        :param cache_control: Value of the Cache-Control HTTP header.
        :return: max-age in seconds as an integer (default: 3600).
        """
        default_max_age = 3600
        if not cache_control:
            return default_max_age

        parts = cache_control.split(',')
        for part in parts:
            part = part.strip()
            if part.startswith('max-age='):
                try:
                    return int(part.split('=')[1])
                except ValueError:
                    pass
        return default_max_age