from urllib import response
import requests
import json
import pytest
from pages.ehr_upload_api_page import EHRUploadApiPage
from pages.appointment_api_page import AppointmentsApiPage
from pages.authorization_api_page import AuthorizationApiPage
from testcases.base_test import BaseTest
from utils.helper import get_formatted_date_str
from utils.request_handler import RequestHandler
import jwt
import allure
import datetime
import re
from utils.dbConfig import DB
from resources.data import Data
from utils.api_request_data_handler import APIRequestDataHandler
from jsonschema.validators import  validate

start_date = get_formatted_date_str(_days=-10, _date_format='%Y-%m-%d')
end_date = get_formatted_date_str(_date_format='%Y-%m-%d')
user_name = pytest.configs.get_config("ehr_upload_non_ehr_provider")
password = pytest.configs.get_config("all_provider_password")
ehr_enabled_doctor = pytest.configs.get_config('ehr_lynx_enabled_rt_provider')
ehr_enabled_doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
doctor_id = pytest.configs.get_config("ehr_upload_non_ehr_provider_id")

class TestEHRUpload(BaseTest):

    def setup_class(self):
        self.ehr_upload = EHRUploadApiPage()
        self.appointments_page = AppointmentsApiPage()
        self.authorization_page = AuthorizationApiPage()
        self.data = Data()
        self.db = DB()

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_upload_a_valid_note_to_ehr(self):
        response_data = self.ehr_upload.get_appointment(user_name=ehr_enabled_doctor,
                                                        password=password,
                                                        doctor_id=ehr_enabled_doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(user_name=ehr_enabled_doctor,
                                                   password=password,
                                                   request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path)
        with allure.step('Proper datalist, status_code and reason should be returned for upload a valid note to ehr'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            assert json_response['code'] == '000'
            assert json_response['dataList'][0]['noteSection'] == 'ROS'
            assert json_response['dataList'][0]['success'] == True
            assert json_response['dataList'][0]['message'] == None
            assert json_response['dataList'][1]['noteSection'] == 'PE'
            assert json_response['dataList'][1]['success'] == True
            assert json_response['dataList'][1]['message'] == None
            assert json_response['dataList'][2]['noteSection'] == 'AP'
            assert json_response['dataList'][2]['success'] == True
            assert json_response['dataList'][2]['message'] == None
        with open('resources/json_data/ehr_upload_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_upload_a_valid_note_to_scp(self):
        response_data, token, headers, note_id = self.appointments_page.create_non_ehr_appointment(user_name=user_name,
                                                                                        password=password,
                                                                                        doctor_id=doctor_id)
        # Authorize the newly created note
        self.authorization_page.create_resource(auth_token=token, note_id=note_id)
        request_path = f'lynx/note/{note_id}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(token=token, headers=headers,
                                                   request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path)
        with allure.step('Proper datalist, status_code and reason should be returned for upload a valid note to scp'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            assert json_response['code'] == '000'
            assert json_response['dataList'][0]['noteSection'] == 'Manual Go note'
            assert json_response['dataList'][0]['success'] == True
            assert "Created note with note id" in json_response['dataList'][0]['message']
        with open('resources/json_data/ehr_upload_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_upload_a_unauthorized_note_to_ehr(self):
        request_path = f'lynx/note/332367d3-351e-4b5d-98b6-cbe77f5cd8bds'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(user_name=ehr_enabled_doctor,
                                                   password=password,
                                                   request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path)
        with allure.step('Proper datalist, status_code and reason should be returned for upload a unauthorized note to ehr'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_upload_a_unauthorized_note_to_scp(self):
        response_data, token, headers, note_id = self.appointments_page.create_non_ehr_appointment(user_name=user_name,
                                                                                        password=password,
                                                                                        doctor_id=doctor_id)
        request_path = f'lynx/note/{note_id}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(token=token, headers=headers,
                                                   request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path)
        with allure.step('Proper datalist, status_code and reason should be returned for upload a unauthorized note to scp'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'
    
    
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_upload_a_note_with_invalid_note_id_to_ehr(self):
        request_path = f'lynx/note/332367d3-351e-4b5d-98b6-'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(user_name=ehr_enabled_doctor,
                                                   password=password,
                                                   request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path)
        with allure.step('Proper datalist, status_code and reason should be returned for upload a note with invalid note id to ehr'):
            assert response.status_code == 500
            assert response.reason == 'Internal Server Error'
            json_response = response.json()
            assert json_response['error'] == 'Internal Server Error'
            assert 'Resource not found' in json_response['message']

    
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_upload_a_valid_note_to_ehr_with_invalid_auth_token(self):
        response_data = self.ehr_upload.get_appointment(user_name=ehr_enabled_doctor,
                                                        password=password,
                                                        doctor_id=ehr_enabled_doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path, 
                                                   token=pytest.configs.get_config('ehr_lynx_enabled_rt_provider_invalid_token'))
        with allure.step('Proper datalist, status_code and reason should be returned for upload a valid note to ehr with invalid auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_upload_a_valid_note_to_ehr_with_expired_auth_token(self):
        response_data = self.ehr_upload.get_appointment(user_name=ehr_enabled_doctor,
                                                        password=password,
                                                        doctor_id=ehr_enabled_doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path, 
                                                   token=pytest.configs.get_config('ehr_lynx_enabled_rt_provider_expired_token'))
        with allure.step('Proper datalist, status_code and reason should be returned for upload a valid note to ehr with expired auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_upload_a_valid_note_to_ehr_with_fake_expired_date_auth_token(self):
        response_data = self.ehr_upload.get_appointment(user_name=ehr_enabled_doctor,
                                                        password=password,
                                                        doctor_id=ehr_enabled_doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path, 
                                                   token=pytest.configs.get_config('ehr_lynx_enabled_rt_provider_fake_expired_date_token'))
        with allure.step('Proper datalist, status_code and reason should be returned for upload a valid note to ehr with fake expired date auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_upload_a_valid_note_to_ehr_with_fake_token_with_valid_provider_auth_token(self):
        response_data = self.ehr_upload.get_appointment(user_name=ehr_enabled_doctor,
                                                        password=password,
                                                        doctor_id=ehr_enabled_doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path, 
                                                   token=pytest.configs.get_config('ehr_lynx_enabled_rt_provider_fake_token_with_valid_provider'))
        with allure.step('Proper datalist, status_code and reason should be returned for upload a valid note to ehr with fake token with valid provider auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_upload_a_valid_note_to_ehr_should_not_be_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        self.doctor_id = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_id")
        token = RequestHandler.get_auth_token(user_name=self.user_name,
                                              password=password)
        response_data = self.ehr_upload.get_appointment(auth_token=token,
                                                        doctor_id=self.doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)

        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.ehr_upload.reset_password(token=token, new_password='@ugmed1X@1')

        response = RequestHandler.get_api_response(request_type='POST',
                                                   payload=payload,
                                                   request_path=request_path,
                                                   token=token)
        with allure.step('Proper create status_code, status_message and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_method_should_not_support_for_upload_a_valid_note_to_ehr(self):
        response_data = self.ehr_upload.get_appointment(user_name=ehr_enabled_doctor,
                                                        password=password,
                                                        doctor_id=ehr_enabled_doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(user_name=ehr_enabled_doctor,
                                                   password=password,
                                                   request_type='GET',
                                                   payload=payload,
                                                   request_path=request_path)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'GET' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_upload_a_valid_note_to_ehr(self):
        response_data = self.ehr_upload.get_appointment(user_name=ehr_enabled_doctor,
                                                        password=password,
                                                        doctor_id=ehr_enabled_doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(user_name=ehr_enabled_doctor,
                                                   password=password,
                                                   request_type='PUT',
                                                   payload=payload,
                                                   request_path=request_path)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_upload_a_valid_note_to_ehr(self):
        response_data = self.ehr_upload.get_appointment(user_name=ehr_enabled_doctor,
                                                        password=password,
                                                        doctor_id=ehr_enabled_doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(user_name=ehr_enabled_doctor,
                                                   password=password,
                                                   request_type='PATCH',
                                                   payload=payload,
                                                   request_path=request_path)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_upload_a_valid_note_to_ehr(self):
        response_data = self.ehr_upload.get_appointment(user_name=ehr_enabled_doctor,
                                                        password=password,
                                                        doctor_id=ehr_enabled_doctor_id)
        uuid = response_data['dataList'][0]['uuid']
        request_path = f'lynx/note/{uuid}'
        request_data = APIRequestDataHandler('ehr_upload_request_body')
        json_payload = request_data.get_payload(name='payload')
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(user_name=ehr_enabled_doctor,
                                                   password=password,
                                                   request_type='DELETE',
                                                   payload=payload,
                                                   request_path=request_path)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"
