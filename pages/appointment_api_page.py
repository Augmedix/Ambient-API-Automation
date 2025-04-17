import datetime
import json
import random
import uuid

import jwt
import pytest
from jwt import DecodeError

from pages.base_page import BasePage
from utils.api_request_data_handler import APIRequestDataHandler
from utils.helper import get_formatted_date_str, get_iso_formatted_datetime_str, get_current_pst_time
from utils.request_handler import RequestHandler
from pages.authorization_api_page import AuthorizationApiPage


class AppointmentsApiPage(BasePage):
    def __init__(self):
        self.authorization_page = AuthorizationApiPage()
    #     super().__init__(db)
    
    base_url = pytest.configs.get_config('appointments_base_url')

    def create_and_get_appointment_note_info(self, user_name, password, auth_token=None, json_payload_name=None,
                                             note_status=0, service_day=2, expiration_day=365):
        request_data = APIRequestDataHandler('appointments_data')
        if auth_token:
            token = auth_token
        else:
            token = RequestHandler.get_auth_token(user_name=user_name,
                                                  password=password)
        headers = request_data.get_modified_headers(Authorization=f'Bearer {token}')

        try:
            token_decoded = jwt.decode(token, options={"verify_signature": False})
            user_guid = token_decoded["guid"]
        except (KeyError, DecodeError) as error:
            user_guid = 'GUID Not Found'

        appointment_id = str(uuid.uuid4())
        patient_id = str(random.randint(1111, 9999))
        creation_date = get_formatted_date_str(_date_format='%Y-%m-%d')
        service_date = get_iso_formatted_datetime_str(_days=service_day)
        expiration_date = get_iso_formatted_datetime_str(_days=expiration_day)
        if json_payload_name == 'bulk_appointments':
            json_payload = request_data.get_modified_payload(name=json_payload_name, serviceDate=service_date,
                                                             expirationDate=expiration_date)
        elif json_payload_name:
            json_payload = request_data.get_modified_payload(name=json_payload_name, appointmentId=appointment_id, patientId=patient_id,
                                                             noteStatus=note_status, serviceDate=service_date,
                                                             expirationDate=expiration_date)
        else:
            json_payload = request_data.get_modified_payload(appointmentId=appointment_id, patientId=patient_id,
                                                             noteStatus=note_status, serviceDate=service_date,
                                                             expirationDate=expiration_date)
        payload = json.dumps(json_payload, indent=4)
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=headers, request_type='POST', payload=payload)
        json_response = response_body.json()
        try:
            note_id = json_response[0]['noteId']
        except KeyError:
            note_id = 'Note ID Not Found'

        return headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date, expiration_date, note_id

    def delete_appointment_note(self, appointment_id, note_id, headers):
        path_appointment_delete = f'appointments/{appointment_id}/notes/{note_id}'
        RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                        request_type='DELETE', headers=headers)

    def create_appointment_using_user_token_and_get_response(self, user_token):
        request_data = APIRequestDataHandler('appointments_data')
        headers = request_data.get_modified_headers(Authorization=f'Bearer {user_token}')
        appointment_id = str(uuid.uuid4())
        json_payload = request_data.get_modified_payload(appointmentId=appointment_id)
        payload = json.dumps(json_payload, indent=4)
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        request_type='POST', headers=headers,
                                                        payload=payload)
        return response_body

    def create_appointment_and_get_update_payload_and_info(self, user_name, password):
        headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.create_and_get_appointment_note_info(
                                                user_name=user_name,
                                                password=password,
                                                json_payload_name='payload')

        request_data = APIRequestDataHandler('appointments_data')
        update_note_status = 1
        json_payload = request_data.get_modified_payload(name="update_note", appointmentId=appointment_id,
                                                         patientId=patient_id, noteStatus=update_note_status,
                                                         serviceDate=service_date, expirationDate=expiration_date)
        update_payload = json.dumps(json_payload, indent=4)
        return token, headers, appointment_id, note_id, update_payload

    
    def create_non_ehr_appointment(self, user_name, password, auth_token=None, doctor_id=None):
        request_data = APIRequestDataHandler('appointments_data')

        if auth_token:
            token = auth_token
        else:
            token = RequestHandler.get_auth_token(user_name=user_name,
                                                  password=password)
        headers = request_data.get_modified_headers(Authorization=f'Bearer {token}')
        print(f"Headers: {headers}")
        print(f"Token: {token}")
        patient_id = str(random.randint(1111, 9999))
        creation_date = get_formatted_date_str(_date_format='%Y-%m-%d')
        current_pst_time = get_current_pst_time()
        json_payload = request_data.get_modified_payload(name='non_ehr_payload',
                                                        startTime=current_pst_time,
                                                        date=creation_date,                                                  
                                                        doctorId=doctor_id,                                                 
                                                        patient={
                                                            "firstName": "Non EHR note" + patient_id,
                                                        }
                                                        )
        updated_payload = json.dumps(json_payload, indent=4)
        path = f'lynx/appointment'
        # Create a non ehr appointment
        response_body = RequestHandler.get_api_response(base_url=pytest.configs.get_config('ehr_base_url'), request_path=path,
                                                        request_type='POST', headers=headers,
                                                        token=token,
                                                        payload=updated_payload)
        json_response = response_body.json()
        note_id = json_response['data']['uuid']
        return json_response, token, headers, note_id

    def create_and_authorize_a_non_ehr_appointment(self, user_name=None, password=None, doctor_id=None, auth_token=None):
        response_data, token, headers, note_id = self.create_non_ehr_appointment(user_name=user_name,
                                                                                password=password,
                                                                                auth_token=auth_token, 
                                                                                doctor_id=doctor_id)
        # Authorize the newly created note
        self.authorization_page.create_resource(auth_token=token, note_id=note_id)
        return response_data, token, headers, note_id



