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

start_date = get_formatted_date_str(_days=3, _date_format='%Y-%m-%d')
end_date = get_formatted_date_str(_date_format='%Y-%m-%d')

class EHRUploadApiPage(BasePage):
    base_url = pytest.configs.get_config('ehr_base_url')

    def get_appointment(self, user_name=None, password=None, doctor_id=None, auth_token=None):
        request_path = f'lynx/appointments?doctorId={doctor_id}&startDate={end_date}&cache.invalidateCache=true&localSearch=false'
        response = RequestHandler.get_api_response(user_name=user_name,
                                                   password=password,
                                                   request_path=request_path,
                                                   token=auth_token)
        json_response = response.json()
        return json_response