# pylint: disable=no-member
import datetime
import jwt
import requests
import json
import pytest
from requests import JSONDecodeError
from utils.api_request_data_handler import APIRequestDataHandler
import os


class RequestHandler:

    @classmethod
    def get_response(cls, base_url=pytest.configs.get_config('ehr_base_url'), request_path='', request_type='GET', headers=None, payload=None):
        """
        Send request to specified url as per request type and returns the response in JSON format.
        :param base_url: Base URL of the API
        :param request_path: Path of the API endpoint
        :param request_type: "GET", "POST", "PUT", "DELETE"
        :param headers: Headers to be sent for the specific request
        :param payload: Data to be sent for the request
        """
        response = requests.request(request_type, f'{base_url}/{request_path}', headers=headers, data=payload)
        return response

    @classmethod
    def get_api_response(cls, base_url=pytest.configs.get_config('ehr_base_url'), request_path='',
                         request_type='GET', headers=None, payload=None, user_name=None, password=None, token=None):
        """
        Send request to specified url as per request type and returns the response in JSON format.
        :param base_url: Base URL of the API
        :param request_path: Path of the API endpoint
        :param request_type: "GET", "POST", "PUT", "DELETE"
        :param headers: Headers to be sent for the specific request
        :param payload: Data to be sent for the request
        :param user_name: Username for authentication
        :param password: Password for authentication
        :param token: Authorization token
        """
        if token:
            auth_token = token
        else:
            auth_token = cls.get_auth_token(user_name=user_name, password=password)

        json_data = APIRequestDataHandler('authentication')

        if not headers:
            headers = json_data.get_modified_headers(Authorization=f'Bearer {auth_token}')

        response = requests.request(request_type, f'{base_url}/{request_path}', headers=headers, data=payload)

        # Debugging information
        print(f'Payload: {payload}')
        print(f'{request_type}: {base_url}/{request_path} -- {response.status_code}')
        try:
            print(f'Response: {json.dumps(response.json(), indent=4)}')
        except JSONDecodeError:
            print(f'Response: {response}')
        return response

    @classmethod
    def get_auth_token(cls, base_url=pytest.configs.get_config('auth_base_url'), user_name=None, password=None):
        """
        Get the authentication token by sending a request to the authentication endpoint.
        :param base_url: Base URL of the authentication API
        :param user_name: Username for authentication
        :param password: Password for authentication
        :return: Authentication token
        """
        response = cls.get_auth_response(base_url=base_url, user_name=user_name, password=password)
        json_response = response.json()
        return json_response.get('token', 'Token Not Found')

    @classmethod
    def get_auth_response(cls, base_url=pytest.configs.get_config('auth_base_url'), request_type='POST',
                          request_path=pytest.configs.get_config('auth_path'), user_name=None, password=None, printData=False):
        """
        Send a request to the authentication endpoint and return the response.
        :param base_url: Base URL of the authentication API
        :param request_type: "POST"
        :param request_path: Path of the authentication endpoint
        :param user_name: Username for authentication
        :param password: Password for authentication
        :param printData: Whether to print debugging information
        :return: Response object
        """
        json_data = APIRequestDataHandler('authentication')
        payload = json_data.get_modified_payload(username=pytest.configs.get_config('lynx_enabled_rt_provider2'),
                                                 password=pytest.configs.get_config('all_provider_password'))
        headers = json_data.get_headers()

        if user_name:
            payload['username'] = user_name
        if password:
            payload['password'] = password

        payload = json.dumps(payload, indent=4)
        response = cls.get_response(request_type=request_type, base_url=base_url,
                                    request_path=request_path, headers=headers, payload=payload)

        if printData:
            print(f'Payload: {payload}')
            print(f'POST: {base_url}/{request_path} -- {response.status_code}')
            try:
                json_response = response.json()
                print(f'Response: {json.dumps(json_response, indent=4)}')
                decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
                print(f'JWT Token Decode: {json.dumps(decoded, indent=4)}')
            except JSONDecodeError:
                print(f'Response: {response}')
            except KeyError:
                pass
            
        return response

    @staticmethod
    def generate_and_save_json_schema(file_path):
        """
        Generate and save JSON schema for audio continuity API.
        :param file_path: Path where the JSON schema will be saved.
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "recordingId": {"type": "string"},
                "title": {"type": "string"},
                "providerId": {"type": "integer"},
                "providerEmail": {"type": "string"},
                "uploadStatus": {"type": "string"},
                "audioLength": {"type": ["integer", "null"]},
                "creationDate": {"type": "string", "format": "date-time"},
                "modifiedDate": {"type": "string", "format": "date-time"},
                "isArchived": {"type": "boolean"},
                "isPlayed": {"type": "boolean"}
            },
            "required": [
                "id",
                "recordingId",
                "title",
                "providerId",
                "providerEmail",
                "uploadStatus",
                "creationDate",
                "modifiedDate",
                "isArchived",
                "isPlayed"
            ]
        }

        # Save the schema to the specified file path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as json_file:
            json.dump(schema, json_file, indent=4)
            print(f"JSON schema saved to {file_path}")

