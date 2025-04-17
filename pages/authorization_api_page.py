import datetime
import json
import random
import uuid

import jwt
import pytest
from jwt import DecodeError

from pages.base_page import BasePage
from utils.api_request_data_handler import APIRequestDataHandler
from utils.helper import get_formatted_date_str
from utils.request_handler import RequestHandler


class AuthorizationApiPage(BasePage):
    # def __init__(self, db):
    #     super().__init__(db)

    base_url = pytest.configs.get_config('authorization_base_url')

    def create_resource(self, user_name=None, password=None, request_type='POST', auth_token=None, note_id=None, authorize_path='authorize'):

        if auth_token:
            token = auth_token
        else:
            token = RequestHandler.get_auth_token(user_name=user_name, password=password)

        request_data = APIRequestDataHandler('authorization')
        headers = request_data.get_modified_headers(Authorization=f'Bearer {token}')
        try:
            token_decoded = jwt.decode(token, options={"verify_signature": False})
            user_guid = token_decoded["guid"]
        except (KeyError, DecodeError) as error:
            user_guid = 'GUID Not Found'
        if note_id:
            resource_id = note_id
        else: 
            resource_id = str(uuid.uuid4())
        json_payload = request_data.get_modified_payload(resourceId=resource_id)
        payload = json.dumps(json_payload, indent=4)

        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=authorize_path,
                                                   request_type=request_type, payload=payload, headers=headers)
        return response, headers, user_guid, resource_id

    def delete_resource(self, resource_id, headers):
        resource_path = f'authorize/{resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE', headers=headers)

