import requests
from time import time

class DIDDocumentCache:
    _cache = {}
    _expiry = {}

    @staticmethod
    def get_did_document(did_url: str) -> dict:
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