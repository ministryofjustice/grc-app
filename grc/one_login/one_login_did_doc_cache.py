import requests
from grc import cache

class DIDDocumentCache:
    """
    Caches DID documents in memory to reduce repeated network calls.
    """

    @staticmethod
    @cache.memoize(timeout=3600)
    def get_did_document(did_url: str) -> dict:
        """
        Retrieves a DID document from cache or fetches it from the given URL.

        :param did_url: The URL of the DID document to fetch.
        :return: Parsed DID document as a dictionary.
        :raises: Exception if fetching fails.
        """
        response = requests.get(did_url)
        response.raise_for_status()
        return response.json()

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