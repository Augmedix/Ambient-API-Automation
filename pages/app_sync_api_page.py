from urllib import response
import jwt
import pytest
from jwt import DecodeError
import json
import random
import uuid
from pages.base_page import BasePage
from utils.api_request_data_handler import APIRequestDataHandler
from utils.helper import get_formatted_date_str
from utils.request_handler import RequestHandler
from pages.appointment_api_page import AppointmentsApiPage


class AppSyncApiPage(BasePage):
    def __init__(self):
        self.appointment = AppointmentsApiPage()
    #     super().__init__(db)

    auth_base_url = pytest.configs.get_config('authorization_base_url')
    ml_base_url = pytest.configs.get_config('ml_base_url')

    def post_transcript(self, user_name, password):
        # Create and get note id and guid
        headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date,\
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(user_name=user_name, password=password)
        request_data = APIRequestDataHandler('authorization')
        json_payload = request_data.get_modified_payload(resourceId=note_id)
        payload = json.dumps(json_payload, indent=4)
        # Authorize an note id
        RequestHandler.get_api_response(base_url=self.auth_base_url, request_path='authorize',
                                                request_type='POST', payload=payload, headers=headers)
        request_data = APIRequestDataHandler('transcript')
        json_payload = request_data.get_modified_payload(note_id=note_id, clinician_id=user_guid)
        payload = json.dumps(json_payload, indent=4)
        # Post a transcript
        response = RequestHandler.get_api_response(base_url=self.ml_base_url, request_path='ml_service',
                                                request_type='POST', payload=payload, headers=headers)
        return headers, user_guid, appointment_id, note_id 
        
        
            