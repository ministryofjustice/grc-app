import abc
import requests
from typing import Dict, Any
from flask import current_app
from grc.utils.logger import Logger, LogLevel

logger = Logger()

class GlimrClientApi(abc.ABC):
    """
    GlimrClientApi is an Abstract Base Class serving as a foundation for calling external GLiMR APIs.

    Retrieves api_key and base_url from environment on initialisation. The specific endpoint to be called
    will be overridden in the endpoint abstract function by subclasses.

    call_api accepts data as an argument, and it will make the api call to GLiMR.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialises API key and base URL.
        """
        self.data = data
        self.api_key = current_app.config['GLIMR_API_KEY']
        self.base_url = current_app.config['GLIMR_BASE_URL']

    @abc.abstractmethod
    def endpoint(self) -> str:
        """
        This should be implemented by subclasses to return the specific endpoint for the API call being made.
        """
        pass

    def get_api_key(self):
        return self.api_key

    def get_base_url(self):
        return self.base_url

    def create_headers(self) -> Dict[str, str]:
        """
        Creates the headers necessary for making the API call. Includes an Authorization header which we pass the api key through.
        """
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'apikey {self.get_api_key()}'
        }

    def make_post_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a POST request to the GLiMR API

        :param endpoint: The API endpoint to send the request to.
        :param data: The data to be sent in the POST request.

        :return: The JSON response from the API.
        :raises Exception: If the request fails.
        """
        url = f'{self.get_base_url()}/{endpoint}'
        headers = self.create_headers()

        try:
            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                logger.log(LogLevel.INFO, f"GLiMR API request to {url} responded with status code 200.")
                return response.json()
            else:
                logger.log(LogLevel.ERROR, f"GLiMR API request to {url} failed with status code {response.status_code}.")
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            logger.log(LogLevel.ERROR, f"GLiMR API request to {url} failed with error {str(e)} in class {self.__class__.__name__}.")
            raise Exception(str(e))


    def call_api(self) -> Dict[str, Any]:
        """
        Calls the API using a POST request and processes the result.

        :param data: The data to send to the API.
        :return: The API response data.
        """
        data = self.data
        endpoint = self.endpoint()
        return self.make_post_request(endpoint, data)
