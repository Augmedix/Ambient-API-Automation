import datetime
from email import header

import jwt
import requests
import json
import pytest
from requests import JSONDecodeError

from utils.api_request_data_handler import APIRequestDataHandler



class RequestHandler:

    @classmethod
    def get_response(cls, base_url=pytest.configs.get_config('ehr_base_url'), request_path='', request_type='GET', headers=None, payload=None):
        """
        Send request to specified url as per request type and returns the response in JSON format.
        :param url - url of the api
        :param request_type - "GET", "POST", "PUT", "DELETE"
        :param headers - To be sent for the specific request
        :param payload - Data to be sent for the request
        """
        response = requests.request(request_type, f'{base_url}/{request_path}', headers=headers, data=payload)
        return response

    @classmethod
    def get_api_response(cls, base_url=pytest.configs.get_config('ehr_base_url'), request_path='',
                         request_type='GET', headers=None, payload=None, user_name=None, password=None, token=None):
        """
        Send request to specified url as per request type and returns the response in JSON format.
        :param url - url of the api
        :param request_type - "GET", "POST", "PUT", "DELETE"
        :param headers - To be sent for the specific request
        :param payload - Data to be sent for the request
        """
        if token:
            auth_token = token
        else:
            auth_token = cls.get_auth_token(user_name=user_name, password=password)

        json_data = APIRequestDataHandler('authentication')

        if not headers:
            headers = json_data.get_modified_headers(Authorization=f'Bearer {auth_token}')

        response = requests.request(request_type, f'{base_url}/{request_path}', headers=headers, data=payload)
        #print(f'Headers:     {headers}')

        print(f'Payload:{payload}')
        print(f'{request_type}:{base_url}/{request_path} --{response.status_code}')
        try:
            print(f'Response:{json.dumps(response.json(), indent=4)}')
        except JSONDecodeError:
            print(f'Response:{response}')
        return response

    @classmethod
    def get_auth_token(cls, base_url=pytest.configs.get_config('auth_base_url'), user_name=None, password=None):
        """
        Send request to specified url as per request type and returns the response in JSON format.
        :param url - url of the api
        :param request_type - "GET", "POST", "PUT", "DELETE"
        :param headers - To be sent for the specific request
        :param payload - Data to be sent for the request
        """
        response = cls.get_auth_response(base_url=base_url, user_name=user_name, password=password)
        json_response = response.json()
        return json_response.get('token', 'Token Not Found')

    @classmethod
    def get_auth_response(cls, base_url=pytest.configs.get_config('auth_base_url'), request_type='POST', request_path=pytest.configs.get_config('auth_path'), user_name=None, password=None, printData=False):
        """
        Send request to specified url as per request type and returns the response in JSON format.
        :param url - url of the api
        :param request_type - "GET", "POST", "PUT", "DELETE"
        :param headers - To be sent for the specific request
        :param payload - Data to be sent for the request
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
            print(f'Payload:{payload}')
            print(f'POST:{base_url}/{request_path} --{response.status_code}')
            try:
                json_response = response.json()
                print(f'Response:{json.dumps(json_response, indent=4)}')
                decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
                print(f'JWT Token Decode:{json.dumps(decoded, indent=4)}')
            except JSONDecodeError:
                print(f'Response:{response}')
            except KeyError:
                pass
            
        return response

