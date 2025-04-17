import random
import uuid
from urllib import response
import requests
import json
import pytest

from resources.data import Data
from testcases.base_test import BaseTest
from utils.api_request_data_handler import APIRequestDataHandler
from utils.dbConfig import DB
from utils.request_handler import RequestHandler
from utils.helper import is_subset, get_formatted_date_str, get_iso_formatted_datetime_str, compare_date_str
from pages.appointment_api_page import AppointmentsApiPage
import jwt
import allure
import datetime
import re
from jsonschema.validators import  validate


class TestAppointments(BaseTest):
    base_url = pytest.configs.get_config('appointments_base_url')
    date_time_pattern = r'\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}.?([0-9]*)Z'
    appointment_id = ''
    headers = ''

    def setup_class(self):
        self.appointment = AppointmentsApiPage()
        self.modification_date = get_formatted_date_str(_date_format='%Y-%m-%d')
        self.service_date = get_formatted_date_str(_days=2, _date_format='%Y-%m-%d')
        self.service_date_range_start = get_formatted_date_str(_days=1, _date_format='%Y-%m-%d')
        self.service_date_range_end = get_formatted_date_str(_days=3, _date_format='%Y-%m-%d')

    def teardown_method(self):
        if self.appointment_id:
            self.appointment.delete_appointment_note(appointment_id=self.appointment_id, note_id=self.appointment_id, headers=self.headers)

    # @pytest.fixture(autouse=True)
    # def setup_testcase(self):
    #     yield

    # @pytest.fixture
    # def setup_testcase_for_user_active_testcases(self):
    #     yield
    #     self.appointment.update_user_status(key_value=pytest.configs.get_config('lynx_enabled_rt_provider'))

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_all_appointments_for_valid_lynx_enabled_rt_token(self):
        headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))

        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            for i in range(len(json_response)):
                assert json_response[i]['providerId'] == user_guid
                assert json_response[i]['appointmentId'] == json_response[i]['noteId']
                assert re.fullmatch(self.date_time_pattern, json_response[i]['serviceDate'])
                assert re.fullmatch(self.date_time_pattern, json_response[i]['expirationDate'])
                assert json_response[i]['modificationDate'] is None or re.fullmatch(self.date_time_pattern, json_response[i]['modificationDate'])
                assert json_response[i]['creationDate'] is None or re.fullmatch(self.date_time_pattern, json_response[i]['creationDate'])
                self.appointment.delete_appointment_note(appointment_id=json_response[i]['appointmentId'],
                                                         note_id=json_response[i]['noteId'],
                                                         headers=headers)
            with open('resources/json_data/appointments_schema.json', 'r') as json_file:
                expected_schema = json.loads(json_file.read())
            with allure.step('json schema is validated'):
                assert validate(json_response, expected_schema) is None

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_create_appointments_with_all_required_field_and_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 201
            assert response_body.reason == 'Created'
            json_response = response_body.json()
            for i in range(len(json_response)):
                assert json_response[i]['appointmentId'] == self.appointment_id
                assert json_response[i]['appointmentId'] == json_response[i]['noteId']
                assert json_response[i]['providerId'] == user_guid
                assert json_response[i]['patientId'] == patient_id
                assert json_response[i]['noteStatus'] == note_status
                assert re.fullmatch(self.date_time_pattern, json_response[i]['serviceDate'])
                assert compare_date_str(json_response[i]['serviceDate'], service_date)
                assert re.fullmatch(self.date_time_pattern, json_response[i]['expirationDate'])
                assert compare_date_str(json_response[i]['expirationDate'], expiration_date)
                assert json_response[i]['modificationDate'] is None
                assert re.fullmatch(self.date_time_pattern, json_response[i]['creationDate'])
                assert json_response[i]['creationDate'].startswith(creation_date)
            with open('resources/json_data/acute_complaints_data_isMobile_true_schema.json', 'r') as json_file:
                expected_schema = json.loads(json_file.read())
            with allure.step('json schema is validated'):
                assert validate(json_response, expected_schema) is None

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_create_bulk_appointments_with_all_required_field_and_valid_lynx_enabled_rt_token(self):
        headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date, \
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                        user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                        password=pytest.configs.get_config("all_provider_password"),
                                                        json_payload_name='bulk_appointments')
        appointment_id = ["0fe51a72-66c1-46b8-926a-ed8ced3f8666", "0fe51a72-66c1-46b8-926a-ed8ced3f9777"]
        patient_id=["1234", "1235"]
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 201
            assert response_body.reason == 'Created'
            json_response = response_body.json()
            for i in range(len(json_response)):
                assert json_response[i]['appointmentId'] == appointment_id[i]
                assert json_response[i]['appointmentId'] == json_response[i]['noteId']
                assert json_response[i]['providerId'] == user_guid
                assert json_response[i]['patientId'] == patient_id[i]
                assert json_response[i]['noteStatus'] == note_status
                assert re.fullmatch(self.date_time_pattern, json_response[i]['serviceDate'])
                assert compare_date_str(json_response[i]['serviceDate'], service_date)
                assert re.fullmatch(self.date_time_pattern, json_response[i]['expirationDate'])
                assert compare_date_str(json_response[i]['expirationDate'], expiration_date)
                assert json_response[i]['modificationDate'] is None
                assert re.fullmatch(self.date_time_pattern, json_response[i]['creationDate'])
                assert json_response[i]['creationDate'].startswith(creation_date)
                self.appointment.delete_appointment_note(appointment_id=json_response[i]['appointmentId'], note_id=json_response[i]['noteId'], headers=headers)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_appointments_should_not_created_without_appointment_id_using_valid_lynx_enabled_rt_token(self):
        token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                              password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('appointments_data')
        headers = request_data.get_modified_headers(Authorization=f'Bearer {token}')
        json_payload = request_data.get_payload()
        del json_payload[0]['appointmentId']
        payload = json.dumps(json_payload, indent=4)
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        request_type='POST', headers=headers, payload=payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 500
            assert response_body.reason == 'Internal Server Error'
            json_response = response_body.json()
            assert json_response['message'] == 'save.arg0[0].appointmentId: AppointmentId can not be empty'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_all_notes_of_appointment_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            for i in range(len(json_response)):
                assert json_response[i]['appointmentId'] == self.appointment_id
                assert json_response[i]['providerId'] == user_guid
                assert json_response[i]['appointmentId'] == json_response[i]['noteId']
                assert json_response[i]['patientId'] == patient_id
                assert 0 <= json_response[i]['noteStatus'] <= 4
                assert re.fullmatch(self.date_time_pattern, json_response[i]['serviceDate'])
                assert compare_date_str(json_response[i]['serviceDate'], service_date)
                assert re.fullmatch(self.date_time_pattern, json_response[i]['expirationDate'])
                assert compare_date_str(json_response[i]['expirationDate'], expiration_date)
                assert re.fullmatch(self.date_time_pattern, json_response[i]['creationDate'])
                assert json_response[i]['creationDate'].startswith(creation_date)
                assert json_response[i]['modificationDate'] is None or re.fullmatch(self.date_time_pattern, json_response[i]['modificationDate'])

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_specific_appointment_note_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            assert json_response['appointmentId'] == self.appointment_id
            assert json_response['providerId'] == user_guid
            assert json_response['appointmentId'] == json_response['noteId']
            assert json_response['patientId'] == patient_id
            assert json_response['noteStatus'] == note_status
            assert re.fullmatch(self.date_time_pattern, json_response['serviceDate'])
            assert compare_date_str(json_response['serviceDate'], service_date)
            assert re.fullmatch(self.date_time_pattern, json_response['expirationDate'])
            assert compare_date_str(json_response['expirationDate'], expiration_date)
            assert re.fullmatch(self.date_time_pattern, json_response['creationDate'])
            assert json_response['creationDate'].startswith(creation_date)
            assert json_response['modificationDate'] is None or re.fullmatch(self.date_time_pattern, json_response['modificationDate'])

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_update_appointment_note_with_set_audio_successfully_uploaded_for_valid_lynx_enabled_rt_token(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        update_note_status = 2
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        json_payload = request_data.get_modified_payload(name="update_note", appointmentId=self.appointment_id,
                                                         patientId=patient_id, noteStatus=update_note_status,
                                                         serviceDate=service_date, expirationDate=expiration_date)
        payload = json.dumps(json_payload, indent=4)
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers, payload=payload)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            assert json_response['appointmentId'] == self.appointment_id
            assert json_response['appointmentId'] == json_response['noteId']
            assert json_response['providerId'] == user_guid
            assert json_response['patientId'] == patient_id
            assert json_response['noteStatus'] == update_note_status
            assert re.fullmatch(self.date_time_pattern, json_response['serviceDate'])
            assert compare_date_str(json_response['serviceDate'], service_date)
            assert re.fullmatch(self.date_time_pattern, json_response['expirationDate'])
            assert compare_date_str(json_response['expirationDate'], expiration_date)
            assert re.fullmatch(self.date_time_pattern, json_response['modificationDate'])
            assert json_response['modificationDate'].startswith(self.modification_date)
            assert re.fullmatch(self.date_time_pattern, json_response['creationDate'])
            assert json_response['creationDate'].startswith(creation_date)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_update_appointment_note_with_set_audio_upload_in_progress_for_valid_lynx_enabled_rt_token(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        update_note_status = 1
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        json_payload = request_data.get_modified_payload(name="update_note", appointmentId=self.appointment_id,
                                                         patientId=patient_id, noteStatus=update_note_status,
                                                         serviceDate=service_date, expirationDate=expiration_date)
        payload = json.dumps(json_payload, indent=4)
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers, payload=payload)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            assert json_response['appointmentId'] == self.appointment_id
            assert json_response['appointmentId'] == json_response['noteId']
            assert json_response['providerId'] == user_guid
            assert json_response['patientId'] == patient_id
            assert json_response['noteStatus'] == update_note_status
            assert re.fullmatch(self.date_time_pattern, json_response['serviceDate'])
            assert compare_date_str(json_response['serviceDate'], service_date)
            assert re.fullmatch(self.date_time_pattern, json_response['expirationDate'])
            assert compare_date_str(json_response['expirationDate'], expiration_date)
            assert re.fullmatch(self.date_time_pattern, json_response['modificationDate'])
            assert json_response['modificationDate'].startswith(self.modification_date)
            assert re.fullmatch(self.date_time_pattern, json_response['creationDate'])
            assert json_response['creationDate'].startswith(creation_date)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_update_appointment_note_with_set_note_successfully_uploaded_for_valid_lynx_enabled_rt_token(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        update_note_status = 4
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        json_payload = request_data.get_modified_payload(name="update_note", appointmentId=self.appointment_id,
                                                         patientId=patient_id, noteStatus=update_note_status,
                                                         serviceDate=service_date, expirationDate=expiration_date)
        payload = json.dumps(json_payload, indent=4)
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers, payload=payload)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            assert json_response['appointmentId'] == self.appointment_id
            assert json_response['appointmentId'] == json_response['noteId']
            assert json_response['providerId'] == user_guid
            assert json_response['patientId'] == patient_id
            assert json_response['noteStatus'] == update_note_status
            assert re.fullmatch(self.date_time_pattern, json_response['serviceDate'])
            assert compare_date_str(json_response['serviceDate'], service_date)
            assert re.fullmatch(self.date_time_pattern, json_response['expirationDate'])
            assert compare_date_str(json_response['expirationDate'], expiration_date)
            assert re.fullmatch(self.date_time_pattern, json_response['modificationDate'])
            assert json_response['modificationDate'].startswith(self.modification_date)
            assert re.fullmatch(self.date_time_pattern, json_response['creationDate'])
            assert json_response['creationDate'].startswith(creation_date)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_update_appointment_note_can_not_be_possible_with_set_note_status_null_for_valid_lynx_enabled_rt_token(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        update_note_status = ""
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        json_payload = request_data.get_modified_payload(name="update_note", appointmentId=self.appointment_id,
                                                         patientId=patient_id, noteStatus=update_note_status,
                                                         serviceDate=service_date, expirationDate=expiration_date)
        payload = json.dumps(json_payload, indent=4)
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers, payload=payload)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 400
            assert response_body.reason == 'Bad Request'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 400
            assert json_response['error'] == 'Bad Request'
            assert "Validation failed for object='appointmentRequest'. Error count: 1" in json_response['message']
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_id}'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_update_appointment_note_can_not_be_possible_with_set_note_status_string_for_valid_lynx_enabled_rt_token(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        update_note_status = 'new'
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        json_payload = request_data.get_modified_payload(name="update_note", appointmentId=self.appointment_id,
                                                         patientId=patient_id, noteStatus=update_note_status,
                                                         serviceDate=service_date, expirationDate=expiration_date)
        payload = json.dumps(json_payload, indent=4)
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers, payload=payload)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 400
            assert response_body.reason == 'Bad Request'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 400
            assert json_response['error'] == 'Bad Request'
            assert "not a valid `java.lang.Integer` value" in json_response['message']
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_id}'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_update_appointment_note_can_not_be_possible_with_set_note_status_less_than_zero_for_valid_lynx_enabled_rt_token(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        update_note_status = -1
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        json_payload = request_data.get_modified_payload(name="update_note", appointmentId=self.appointment_id,
                                                         patientId=patient_id, noteStatus=update_note_status,
                                                         serviceDate=service_date, expirationDate=expiration_date)
        payload = json.dumps(json_payload, indent=4)
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers, payload=payload)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 400
            assert response_body.reason == 'Bad Request'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 400
            assert json_response['error'] == 'Bad Request'
            assert "Validation failed for object='appointmentRequest'. Error count: 1" in json_response['message']
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_id}'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_update_appointment_note_can_not_be_possible_with_set_note_status_greater_than_four_for_valid_lynx_enabled_rt_token(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        update_note_status = 5
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        json_payload = request_data.get_modified_payload(name="update_note", appointmentId=self.appointment_id,
                                                         patientId=patient_id, noteStatus=update_note_status,
                                                         serviceDate=service_date, expirationDate=expiration_date)
        payload = json.dumps(json_payload, indent=4)
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers, payload=payload)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 400
            assert response_body.reason == 'Bad Request'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 400
            assert json_response['error'] == 'Bad Request'
            assert "Validation failed for object='appointmentRequest'. Error count: 1" in json_response['message']
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_id}'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_patch_appointment_note_status_set_audio_upload_in_progress_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        note_status_update = 1
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            assert json_response['noteStatus'] == note_status_update
            assert json_response['appointmentId'] == self.appointment_id
            assert json_response['appointmentId'] == json_response['noteId']
            assert json_response['providerId'] == user_guid
            assert json_response['patientId'] == patient_id
            assert re.fullmatch(self.date_time_pattern, json_response['serviceDate'])
            assert compare_date_str(json_response['serviceDate'], service_date)
            assert re.fullmatch(self.date_time_pattern, json_response['expirationDate'])
            assert compare_date_str(json_response['expirationDate'], expiration_date)
            assert re.fullmatch(self.date_time_pattern, json_response['modificationDate'])
            assert json_response['modificationDate'].startswith(self.modification_date)
            assert re.fullmatch(self.date_time_pattern, json_response['creationDate'])
            assert json_response['creationDate'].startswith(creation_date)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_patch_appointment_note_status_set_audio_successfully_uploaded_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        note_status_update = 2
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            assert json_response['noteStatus'] == note_status_update
            assert json_response['appointmentId'] == self.appointment_id
            assert json_response['appointmentId'] == json_response['noteId']
            assert json_response['providerId'] == user_guid
            assert json_response['patientId'] == patient_id
            assert re.fullmatch(self.date_time_pattern, json_response['serviceDate'])
            assert compare_date_str(json_response['serviceDate'], service_date)
            assert re.fullmatch(self.date_time_pattern, json_response['expirationDate'])
            assert compare_date_str(json_response['expirationDate'], expiration_date)
            assert re.fullmatch(self.date_time_pattern, json_response['modificationDate'])
            assert json_response['modificationDate'].startswith(self.modification_date)
            assert re.fullmatch(self.date_time_pattern, json_response['creationDate'])
            assert json_response['creationDate'].startswith(creation_date)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_patch_appointment_note_status_set_note_successfully_uploaded_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date, \
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                            user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        note_status_update = 4
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            assert json_response['noteStatus'] == note_status_update
            assert json_response['appointmentId'] == self.appointment_id
            assert json_response['appointmentId'] == json_response['noteId']
            assert json_response['providerId'] == user_guid
            assert json_response['patientId'] == patient_id
            assert re.fullmatch(self.date_time_pattern, json_response['serviceDate'])
            assert compare_date_str(json_response['serviceDate'], service_date)
            assert re.fullmatch(self.date_time_pattern, json_response['expirationDate'])
            assert compare_date_str(json_response['expirationDate'], expiration_date)
            assert re.fullmatch(self.date_time_pattern, json_response['modificationDate'])
            assert json_response['modificationDate'].startswith(self.modification_date)
            assert re.fullmatch(self.date_time_pattern, json_response['creationDate'])
            assert json_response['creationDate'].startswith(creation_date)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_patch_appointment_note_status_can_not_be_set_less_than_integer_0_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date, \
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                                password=pytest.configs.get_config("all_provider_password"))
        invalid_note_status = -1
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{invalid_note_status}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_patch,
                                                            request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 500
            assert response_body.reason == 'Internal Server Error'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert "Value must be greater than or equal to 0 and less than or equal  to 4" in json_response['message']
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_id}/{invalid_note_status}'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_patch_appointment_note_status_can_not_be_set_greater_than_integer_4_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date, \
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                                password=pytest.configs.get_config("all_provider_password"))

        invalid_note_status = 5
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{invalid_note_status}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_patch,
                                                            request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 500
            assert response_body.reason == 'Internal Server Error'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert "Value must be greater than or equal to 0 and less than or equal  to 4" in json_response['message']
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_id}/{invalid_note_status}'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_patch_appointment_note_status_can_not_be_set_as_string_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date, \
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                                password=pytest.configs.get_config("all_provider_password"))

        invalid_note_status = 'new'
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{invalid_note_status}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_patch,
                                                            request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 400
            assert response_body.reason == 'Bad Request'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 400
            assert json_response['error'] == 'Bad Request'
            assert "Failed to convert value of type 'java.lang.String' to required type 'java.lang.Integer'" in json_response['message']
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_id}/{invalid_note_status}'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_patch_note_status_should_not_be_possible_without_appointment_id_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        note_status_update = 1
        path_appointment_patch_without_appointment_id = f'appointments/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch_without_appointment_id,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 404
            assert response_body.reason == 'Not Found'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == 'No message available'
            assert json_response['path'] == f'/appointments/notes/{note_id}/{note_status_update}'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_patch_note_status_should_not_be_possible_without_note_id_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        note_status_update = 1
        path_appointment_patch_without_note_id = f'appointments/{self.appointment_id}/notes/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch_without_note_id,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_status_update}'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_patch_note_status_should_not_be_possible_without_node_status_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        path_appointment_patch_without_note_status = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch_without_note_status,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_id}'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_patch_note_status_should_not_be_possible_with_invalid_appointment_id_valid_note_id_and_status_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        note_status_update = 1
        path_appointment_patch_with_invalid_appointment_id = f'appointments/{self.appointment_id[:-5]}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch_with_invalid_appointment_id,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 404
            assert response_body.reason == 'Not Found'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == "Appointment not found"
            assert json_response['path'] == f'/appointments/{self.appointment_id[:-5]}/notes/{note_id}/{note_status_update}'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_patch_note_status_should_not_be_possible_with_invalid_note_id_valid_appointment_id_and_status_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        note_status_update = 1
        path_appointment_patch_with_invalid_note_id = f'appointments/{self.appointment_id}/notes/{note_id[:-6]}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch_with_invalid_note_id,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 404
            assert response_body.reason == 'Not Found'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == "Appointment not found"
            assert json_response['path'] == f'/appointments/{self.appointment_id}/notes/{note_id[:-6]}/{note_status_update}'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_patch_note_status_should_not_be_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        note_status_update = 1
        invalid_token = pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {invalid_token}')
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=headers_with_invalid_token)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_patch_note_status_should_not_be_possible_with_lynx_enabled_rt_provider_expired_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        note_status_update = 1
        expired_token = pytest.configs.get_config('provider_expired_auth_token')
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {expired_token}')
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=headers_with_expired_token)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_all_appointments_by_note_service_date_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id= self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            for i in range(len(json_response)):
                assert json_response[i]['providerId'] == user_guid
                assert json_response[i]['serviceDate'].startswith(self.service_date)
                assert re.fullmatch(self.date_time_pattern, json_response[i]['serviceDate'])
                assert json_response[i]['patientId']
                assert 0 <= json_response[i]['noteStatus'] <= 4
                assert json_response[i]['appointmentId'] == json_response[i]['noteId']
                assert re.fullmatch(self.date_time_pattern, json_response[i]['expirationDate'])
                assert json_response[i]['modificationDate'] is None or re.fullmatch(self.date_time_pattern, json_response[i]['modificationDate'])
                assert re.fullmatch(self.date_time_pattern, json_response[i]['creationDate'])

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_all_appointments_by_note_service_date_range_for_valid_lynx_enabled_rt_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        service_date_range_mid = get_formatted_date_str(_days=2, _date_format='%Y-%m-%d')
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            for i in range(len(json_response)):
                assert json_response[i]['providerId'] == user_guid
                assert json_response[i]['serviceDate'].startswith(self.service_date_range_start) or \
                       json_response[i]['serviceDate'].startswith(service_date_range_mid) or \
                       json_response[i]['serviceDate'].startswith(self.service_date_range_end)
                assert re.fullmatch(self.date_time_pattern, json_response[i]['serviceDate'])
                assert json_response[i]['patientId']
                assert 0 <= json_response[i]['noteStatus'] <=4
                assert json_response[i]['appointmentId'] == json_response[i]['noteId']
                assert re.fullmatch(self.date_time_pattern, json_response[i]['expirationDate'])
                assert json_response[i]['modificationDate'] is None or re.fullmatch(self.date_time_pattern, json_response[i]['modificationDate'])
                assert re.fullmatch(self.date_time_pattern, json_response[i]['creationDate'])

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_delete_appointment_note_for_valid_lynx_enabled_rt_token(self):
        headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))

        path_appointment_delete = f'appointments/{appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        request_type='DELETE', headers=headers)

        with allure.step('Proper status_code and reason should be returned'):
            assert response_body.status_code == 204
            assert response_body.reason == 'No Content'

        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        headers=headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 404
            assert response_body.reason == 'Not Found'
            json_response = response_body.json()
            assert json_response['message'] == 'Appointment not found'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                              password=pytest.configs.get_config("all_provider_password"))

        invalid_token = pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token")
        response_body = self.appointment.create_appointment_using_user_token_and_get_response(invalid_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_expired_token(self):
        expired_token = pytest.configs.get_config("lynx_enabled_rt_provider_expired_token")
        response_body = self.appointment.create_appointment_using_user_token_and_get_response(expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_appointment_should_not_be_possible_with_algorithm_set_as_none_token(self):
        token_with_algorithm_set_as_none = pytest.configs.get_config("token_with_algorithm_set_as_none")
        response_body = self.appointment.create_appointment_using_user_token_and_get_response(token_with_algorithm_set_as_none)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_security_create_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        token = RequestHandler.get_auth_token(user_name=self.user_name,
                                              password=pytest.configs.get_config("all_provider_password"))
        # self.appointment.blocked_user(pytest.configs.get_config("lynx_enabled_rt_provider"))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')

        response_body = self.appointment.create_appointment_using_user_token_and_get_response(token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
        # self.appointment.update_user_status(key_value=pytest.configs.get_config("lynx_enabled_rt_provider"))

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_appointment_should_not_be_possible_with_lynx_disabled_rt_provider_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        response_body = self.appointment.create_appointment_using_user_token_and_get_response(lynx_disabled_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 500
            assert response_body.reason == 'Internal Server Error'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert json_response['message'].find("reading AuthorizationApi#create(List);")
            assert json_response['path'] == f'/appointments'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        invalid_token = pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {invalid_token}')
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=headers_with_invalid_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_expired_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        expired_token = pytest.configs.get_config("lynx_enabled_rt_provider_expired_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {expired_token}')
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_appointment_should_not_be_possible_with_algorithm_set_as_none_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        token_with_algorithm_set_as_none = pytest.configs.get_config("token_with_algorithm_set_as_none")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {token_with_algorithm_set_as_none}')
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_security_get_all_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        # self.appointment.blocked_user(pytest.configs.get_config("lynx_enabled_rt_provider"))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')

        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=self.headers)

        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
        # self.appointment.update_user_status(key_value=pytest.configs.get_config("lynx_enabled_rt_provider"))
        # self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_appointment_should_not_be_possible_with_lynx_disabled_rt_provider_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_lynx_disabled_token = request_data.get_modified_headers(Authorization=f'Bearer {lynx_disabled_token}')
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=headers_with_lynx_disabled_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 404
            assert response_body.reason == 'Not Found'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == 'Token GUID not found'
            assert json_response['path'] == f'/appointments'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_notes_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        invalid_token = pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {invalid_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_invalid_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_notes_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_expired_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        expired_token = pytest.configs.get_config("lynx_enabled_rt_provider_expired_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {expired_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
    
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_notes_of_appointment_should_not_be_possible_with_algorithm_set_as_none_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        token_with_algorithm_set_as_none = pytest.configs.get_config("token_with_algorithm_set_as_none")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {token_with_algorithm_set_as_none}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_security_get_all_notes_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        # self.appointment.blocked_user(pytest.configs.get_config("lynx_enabled_rt_provider"))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')

        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
        # self.appointment.update_user_status(key_value=pytest.configs.get_config("lynx_enabled_rt_provider"))
        # self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_notes_of_appointment_should_not_be_possible_with_lynx_disabled_rt_provider_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_lynx_disabled_token = request_data.get_modified_headers(Authorization=f'Bearer {lynx_disabled_token}')

        path_appointment_notes = f'appointments/0fe51a72-66c1-46b8-926a-ed8ced3f6b48/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_lynx_disabled_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_specific_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        invalid_token = pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {invalid_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_invalid_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_specific_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_expired_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        expired_token = pytest.configs.get_config("lynx_enabled_rt_provider_expired_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {expired_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_specific_note_of_appointment_should_not_be_possible_with_algorithm_set_as_none_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        token_with_algorithm_set_as_none = pytest.configs.get_config("token_with_algorithm_set_as_none")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {token_with_algorithm_set_as_none}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_get_specific_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        # self.appointment.blocked_user(pytest.configs.get_config("lynx_enabled_rt_provider"))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
        # self.appointment.update_user_status(key_value=pytest.configs.get_config("lynx_enabled_rt_provider"))
        # self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_specific_note_of_appointment_should_not_be_possible_with_lynx_disabled_rt_provider_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_lynx_disabled_token = request_data.get_modified_headers(Authorization=f'Bearer {lynx_disabled_token}')

        path_appointment_notes = \
            f'appointments/0fe51a72-66c1-46b8-926a-ed8ced3f6b48/notes/0fe51a72-66c1-46b8-926a-ed8ced3f6b48'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_lynx_disabled_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_update_specific_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                            self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        invalid_token = pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {invalid_token}')

        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=headers_with_invalid_token,
                                                        payload=update_payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_update_specific_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_expired_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        expired_token = pytest.configs.get_config("lynx_enabled_rt_provider_expired_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {expired_token}')

        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=headers_with_expired_token,
                                                        payload=update_payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
    
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_update_specific_note_of_appointment_should_not_be_possible_with_algorithm_set_as_none_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        token_with_algorithm_set_as_none = pytest.configs.get_config("token_with_algorithm_set_as_none")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {token_with_algorithm_set_as_none}')
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=headers_with_expired_token,
                                                        payload=update_payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
    
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_update_specific_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        # self.appointment.blocked_user(pytest.configs.get_config("lynx_enabled_rt_provider"))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers,
                                                        payload=update_payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
        # self.appointment.update_user_status(key_value=pytest.configs.get_config("lynx_enabled_rt_provider"))
        # self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_update_specific_note_of_appointment_should_not_be_possible_with_lynx_disabled_rt_provider_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_lynx_disabled_token = request_data.get_modified_headers(Authorization=f'Bearer {lynx_disabled_token}')

        update_note_status = 2
        json_payload = request_data.get_modified_payload(name="update_note", noteStatus=update_note_status)
        update_payload = json.dumps(json_payload, indent=4)

        path_appointment_update = \
            f'appointments/0fe51a72-66c1-46b8-926a-ed8ced3f6b48/notes/0fe51a72-66c1-46b8-926a-ed8ced3f6b48'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=headers_with_lynx_disabled_token,
                                                        payload=update_payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                            self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        invalid_token = pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {invalid_token}')

        path_appointment_delete = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        request_type='DELETE', headers=headers_with_invalid_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_expired_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        expired_token = pytest.configs.get_config("lynx_enabled_rt_provider_expired_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {expired_token}')

        path_appointment_delete = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        request_type='DELETE', headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_note_of_appointment_should_not_be_possible_with_algorithm_set_as_none_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        token_with_algorithm_set_as_none = pytest.configs.get_config("token_with_algorithm_set_as_none")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {token_with_algorithm_set_as_none}')

        path_appointment_delete = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        request_type='DELETE', headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_delete_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        # self.appointment.blocked_user(pytest.configs.get_config("lynx_enabled_rt_provider"))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        path_appointment_delete = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        request_type='DELETE', headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
        # self.appointment.update_user_status(key_value=pytest.configs.get_config("lynx_enabled_rt_provider"))
        # self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_note_of_appointment_should_not_be_possible_with_lynx_disabled_rt_provider_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_lynx_disabled_token = request_data.get_modified_headers(Authorization=f'Bearer {lynx_disabled_token}')

        path_appointment_update = \
            f'appointments/0fe51a72-66c1-46b8-926a-ed8ced3f6b48/notes/0fe51a72-66c1-46b8-926a-ed8ced3f6b48'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='DELETE', headers=headers_with_lynx_disabled_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_update_note_status_should_not_be_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        # self.appointment.blocked_user(pytest.configs.get_config("lynx_enabled_rt_provider"))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        note_status_update = 1
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
        # self.appointment.update_user_status(key_value=pytest.configs.get_config("lynx_enabled_rt_provider"))
        # self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_update_note_status_of_should_not_be_possible_with_lynx_disabled_rt_provider_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_lynx_disabled_token = request_data.get_modified_headers(Authorization=f'Bearer {lynx_disabled_token}')

        note_status_update = 1
        path_appointment_patch = f'appointments/0fe51a72-66c1-46b8-926a-ed8ced3f6b48/notes/0fe51a72-66c1-46b8-926a-ed8ced3f6b48/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=headers_with_lynx_disabled_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_should_not_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        invalid_token = pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {invalid_token}')
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_invalid_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_should_not_possible_with_lynx_enabled_rt_provider_expired_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        expired_token = pytest.configs.get_config("lynx_enabled_rt_provider_expired_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {expired_token}')
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_should_not_possible_with_algorithm_set_as_none_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        token_with_algorithm_set_as_none = pytest.configs.get_config("token_with_algorithm_set_as_none")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {token_with_algorithm_set_as_none}')
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_should_not_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        # self.appointment.blocked_user(pytest.configs.get_config("lynx_enabled_rt_provider"))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

        # self.appointment.update_user_status(key_value=pytest.configs.get_config("lynx_enabled_rt_provider"))
        # self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_should_not_possible_with_lynx_disabled_rt_provider_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_lynx_disabled_token = request_data.get_modified_headers(Authorization=f'Bearer {lynx_disabled_token}')

        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_lynx_disabled_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 404
            assert response_body.reason == 'Not Found'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == 'Token GUID not found'
            assert json_response['path'] == f'/appointments/{self.service_date}'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_range_should_not_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        invalid_token = pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {invalid_token}')
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_invalid_token)

        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_range_should_not_possible_with_lynx_enabled_rt_provider_expired_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        expired_token = pytest.configs.get_config("lynx_enabled_rt_provider_expired_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {expired_token}')
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_get_appointment_note_by_service_date_range_should_not_possible_with_algorithm_set_as_none_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        token_with_algorithm_set_as_none = pytest.configs.get_config("token_with_algorithm_set_as_none")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {token_with_algorithm_set_as_none}')
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_range_should_not_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        # self.appointment.blocked_user(pytest.configs.get_config("lynx_enabled_rt_provider"))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
        # self.appointment.update_user_status(key_value=pytest.configs.get_config("lynx_enabled_rt_provider"))
        # self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_range_should_not_possible_with_lynx_disabled_rt_provider_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_lynx_disabled_token = request_data.get_modified_headers(Authorization=f'Bearer {lynx_disabled_token}')
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_lynx_disabled_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 404
            assert response_body.reason == 'Not Found'
            json_response = response_body.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == 'Token GUID not found'
            assert json_response['path'] == f'/appointments/{self.service_date_range_start}/{self.service_date_range_end}'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_fake_expired_date_token(self):
        fake_expired_date_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_expired_date_token")
        response_body = self.appointment.create_appointment_using_user_token_and_get_response(fake_expired_date_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_fake_expired_date_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_expired_date_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_expired_date_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_expired_date_token}')
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=headers_with_fake_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_notes_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_fake_expired_date_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_expired_date_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_expired_date_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_expired_date_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_fake_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_specific_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_fake_expired_date_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_expired_date_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_expired_date_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_expired_date_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_fake_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_update_specific_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_fake_expired_date_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        fake_expired_date_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_expired_date_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_expired_date_token}')
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=headers_with_fake_expired_token,
                                                        payload=update_payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_patch_note_status_should_not_be_possible_with_lynx_enabled_rt_provider_fake_expired_date_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        note_status_update = 1
        fake_expired_date_token = pytest.configs.get_config('lynx_enabled_rt_provider_fake_expired_date_token')
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_expired_date_token}')
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=headers_with_fake_expired_token)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_note_of_appointment_should_not_be_possible_with_lynx_enabled_rt_provider_fake_expired_date_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        fake_expired_date_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_expired_date_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_expired_date_token}')

        path_appointment_delete = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        request_type='DELETE', headers=headers_with_fake_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_should_not_possible_with_lynx_enabled_rt_provider_fake_expired_date_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_expired_date_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_expired_date_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_expired_date_token}')
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_fake_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_range_should_not_possible_with_lynx_enabled_rt_provider_fake_expired_date_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_expired_date_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_expired_date_token")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_expired_date_token}')
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_fake_expired_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_appointment_should_not_be_possible_with_fake_token_with_valid_provider(self):
        fake_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_token_with_valid_provider")
        response_body = self.appointment.create_appointment_using_user_token_and_get_response(fake_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_appointment_should_not_be_possible_with_fake_token_with_valid_provider(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_token_with_valid_provider")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_token}')
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=headers_with_fake_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_notes_of_appointment_should_not_be_possible_with_fake_token_with_valid_provider(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_token_with_valid_provider")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_fake_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_specific_note_of_appointment_should_not_be_possible_with_fake_token_with_valid_provider(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_token_with_valid_provider")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_fake_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_update_specific_note_of_appointment_should_not_be_possible_with_fake_token_with_valid_provider(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        fake_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_token_with_valid_provider")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_token}')

        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=headers_with_fake_token,
                                                        payload=update_payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_patch_note_status_should_not_be_possible_with_fake_token_with_valid_provider(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        note_status_update = 1
        fake_token = pytest.configs.get_config('lynx_enabled_rt_provider_fake_token_with_valid_provider')
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_token}')
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=headers_with_fake_token)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_note_of_appointment_should_not_be_possible_with_fake_token_with_valid_provider(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        fake_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_token_with_valid_provider")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_token}')

        path_appointment_delete = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        request_type='DELETE', headers=headers_with_fake_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_should_not_possible_with_fake_token_with_valid_provider(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_token_with_valid_provider")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_token}')
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_fake_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_range_should_not_possible_with_fake_token_with_valid_provider(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        fake_token = pytest.configs.get_config("lynx_enabled_rt_provider_fake_token_with_valid_provider")
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_fake_token = request_data.get_modified_headers(Authorization=f'Bearer {fake_token}')
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=headers_with_fake_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_all_notes_of_appointment_should_not_be_possible_with_different_lynx_enabled_rt_provider_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        different_user_token = RequestHandler.get_auth_token(
                                                    user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_different_user_token = request_data.get_modified_headers(Authorization=f'Bearer {different_user_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_different_user_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_specific_note_of_appointment_should_not_be_possible_with_different_lynx_enabled_rt_provider_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        different_user_token = RequestHandler.get_auth_token(
                                                    user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_different_user_token = request_data.get_modified_headers(Authorization=f'Bearer {different_user_token}')
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=headers_with_different_user_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_update_specific_note_of_appointment_should_not_be_possible_with_different_lynx_enabled_rt_provider_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        different_user_token = RequestHandler.get_auth_token(
                                                    user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_different_user_token = request_data.get_modified_headers(Authorization=f'Bearer {different_user_token}')

        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=headers_with_different_user_token,
                                                        payload=update_payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_patch_note_status_should_not_be_possible_with_different_lynx_enabled_rt_provider_token(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                note_status= 1)
        note_status_update = 1
        different_user_token = RequestHandler.get_auth_token(
                                                    user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_different_user_token = request_data.get_modified_headers(Authorization=f'Bearer {different_user_token}')
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=headers_with_different_user_token)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_note_of_appointment_should_not_be_possible_with_different_lynx_enabled_rt_provider_token(self):
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                    user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"))
        different_user_token = RequestHandler.get_auth_token(
                                                    user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'))
        request_data = APIRequestDataHandler('appointments_data')
        headers_with_different_user_token = request_data.get_modified_headers(Authorization=f'Bearer {different_user_token}')

        path_appointment_delete = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        request_type='DELETE', headers=headers_with_different_user_token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_all_appointments_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        request_type='PUT',
                                                        headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_all_appointments_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        request_type='PATCH',
                                                        headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_get_all_appointments_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        request_type='DELETE',
                                                        headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_all_notes_of_appointment_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        request_type='PUT',
                                                        headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_all_notes_of_appointment_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        request_type='POST',
                                                        headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_all_notes_of_appointment_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        request_type='PATCH',
                                                        headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_get_all_notes_of_appointment_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        request_type='DELETE',
                                                        headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_specific_appointment_note_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        request_type='POST',
                                                        headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_specific_appointment_note_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        request_type='PATCH',
                                                        headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_method_should_not_support_for_update_appointment_note_endpoint(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}/test'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='GET', headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'GET' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_update_appointment_note_endpoint(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}/test'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='POST', headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_update_appointment_note_endpoint(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}/test'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_update_appointment_note_endpoint(self):
        request_data = APIRequestDataHandler('appointments_data')
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"),
                                                json_payload_name='payload')
        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}/test'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='DELETE', headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_all_appointments_by_note_service_date_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id= self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_type='POST',
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_all_appointments_by_note_service_date_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id= self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_type='PUT',
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_all_appointments_by_note_service_date_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id= self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_type='PATCH',
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_get_all_appointments_by_note_service_date_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id= self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_type='DELETE',
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_all_appointments_by_note_service_date_range_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_type='POST',
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_all_appointments_by_note_service_date_range_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_type='PUT',
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_all_appointments_by_note_service_date_range_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_type='PATCH',
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_get_all_appointments_by_note_service_date_range_endpoint(self):
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_type='DELETE',
                                                        request_path=path_appointment_specific_date, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response_body.status_code == 405
            assert response_body.reason == 'Method Not Allowed'
            json_response = response_body.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_create_appointment_should_not_be_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        token = RequestHandler.get_auth_token(user_name=self.user_name,
                                              password=pytest.configs.get_config("all_provider_password"))

        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')
        response_body = self.appointment.create_appointment_using_user_token_and_get_response(token)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_get_all_appointment_should_not_be_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date, \
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(user_name=self.user_name,
                                                                        password=pytest.configs.get_config("all_provider_password"))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')

        appointments_path = 'appointments'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=appointments_path,
                                                        headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_get_all_notes_of_appointment_should_not_be_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date, \
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(user_name=self.user_name,
                                                            password=pytest.configs.get_config("all_provider_password"))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')

        path_appointment_notes = f'appointments/{self.appointment_id}/notes'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_get_specific_note_of_appointment_should_not_be_possible_with_changed_password_previous_token(
            self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date, \
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                            user_name=self.user_name,
                                                            password=pytest.configs.get_config("all_provider_password"))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')

        path_appointment_notes = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_notes,
                                                        headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_update_specific_note_of_appointment_should_not_be_possible_with_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')

        path_appointment_update = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_update,
                                                        request_type='PUT', headers=self.headers,
                                                        payload=update_payload)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_delete_note_of_appointment_should_not_be_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')
        path_appointment_delete = f'appointments/{self.appointment_id}/notes/{note_id}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url, request_path=path_appointment_delete,
                                                        request_type='DELETE', headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_update_note_status_should_not_be_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        token, self.headers, self.appointment_id, note_id, update_payload = \
                                                self.appointment.create_appointment_and_get_update_payload_and_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')
        note_status_update = 1
        path_appointment_patch = f'appointments/{self.appointment_id}/notes/{note_id}/{note_status_update}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_patch,
                                                        request_type='PATCH', headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_should_not_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')
        path_appointment_specific_date = f'appointments/{self.service_date}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_get_appointment_note_by_service_date_range_should_not_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        self.headers, token, user_guid, response_body, self.appointment_id, patient_id, note_status, creation_date, service_date,\
            expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config("all_provider_password"))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')
        path_appointment_specific_date = f'appointments/{self.service_date_range_start}/{self.service_date_range_end}'
        response_body = RequestHandler.get_api_response(base_url=self.base_url,
                                                        request_path=path_appointment_specific_date,
                                                        headers=self.headers)
        with allure.step('Proper message, status_code and reason should be returned'):
            assert response_body.status_code == 401
            assert response_body.reason == 'Unauthorized'
