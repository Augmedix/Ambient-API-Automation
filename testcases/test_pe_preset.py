import requests
import json
import pytest
from pages.transcript_api_page import TranscriptApiPage
from pages.appointment_api_page import AppointmentsApiPage
from pages.authorization_api_page import AuthorizationApiPage
from pages.ehr_upload_api_page import EHRUploadApiPage
from testcases.base_test import BaseTest
from utils.helper import get_formatted_date_str, compare_date_str
from utils.request_handler import RequestHandler
import jwt
import allure
import datetime
import re
from utils.dbConfig import DB
from resources.data import Data
from utils.api_request_data_handler import APIRequestDataHandler
from jsonschema.validators import validate
from utils.upload_go_audio.upload_audio import upload_audio_to_go_note
import time
import jsondiff


class TestPEPreset(BaseTest):
    """
    Test class for handling PE presets
    """
    pe_preset_base_url = pytest.configs.get_config('pe_preset_url')
    apply_pe_preset_base_url = pytest.configs.get_config('apply_pe_preset_base_url')
    user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
    password = pytest.configs.get_config("all_provider_password")
    doctor_id = pytest.configs.get_config("lynx_enabled_rt_provider_id")
    ehr_enabled_doctor = pytest.configs.get_config('ehr_lynx_enabled_rt_provider')
    ehr_enabled_doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
    date_time_pattern = r'\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}.?([0-9]*)'
    get_pe_preset_request_path = f'users/providers/{doctor_id}/pe-template/presets'
    # ... other class variables ...
    noteId = ''
    provider_preset_id = 6243
    invalid_provider_preset_id = 123456
    unassigned_preset_id = 1529
    stream_id = ''
    second_appointment_id = ''
    second_note_id = ''
    ehr_enabled_note_stream_id = ''
    ehr_enabled_note_id = ''
    auth_token = ''
    
    #headers = ''


    def setup_class(self):
        """
        Setting up the test environment.
        """
        self.transcript_page = TranscriptApiPage()
        self.data = Data()
        self.db = DB()
        self.appointments_page = AppointmentsApiPage()
        self.authorization_page = AuthorizationApiPage()
        self.ehr_upload_page = EHRUploadApiPage()
        """
        Test creating and authorizing a non-EHR appointment.
        """
        # Create and authorize an appointment, and retrieve necessary data
        self.response_data, self.token, self.headers, self.note_id = self.appointments_page.create_and_authorize_a_non_ehr_appointment(
            user_name=self.user_name,
            password=self.password,
            doctor_id=self.doctor_id
        )

        # Store the note ID and token for later use
        TestPEPreset.noteId = self.note_id
        TestPEPreset.auth_token = self.token

        


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_assigned_pe_preset_of_an_doctor(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url,
                                                   user_name=self.user_name,
                                                   password=self.password,
                                                   request_path=self.get_pe_preset_request_path)
        with allure.step('Proper datalist, status_code and reason should be returned for get assigned pe preset of a doctor'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
        with open('resources/json_data/pe_preset_response.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
            assert json_response == expected_response
        with open('resources/json_data/pe_preset_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_get_assigned_pe_preset_of_an_doctor_with_invalid_auth_token(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, request_path=self.get_pe_preset_request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_invalid_token'))
        with allure.step('Proper error message should be returned for try to get assigned pe preset of a doctor with invalid auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_get_assigned_pe_preset_of_an_doctor_with_expired_auth_token(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, request_path=self.get_pe_preset_request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_expired_token'))
        with allure.step('Proper error message should be returned for try to get assigned pe preset of a doctor with expired auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_get_assigned_pe_preset_of_an_doctor_with_fake_expired_date_auth_token(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, request_path=self.get_pe_preset_request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_expired_date_token'))
        with allure.step('Proper error message should be returned for try to get assigned pe preset of a doctor with fake expired date auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_get_assigned_pe_preset_of_an_doctor_with_fake_token_with_valid_provider_token(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, request_path=self.get_pe_preset_request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_token_with_valid_provider'))
        with allure.step('Proper error message should be returned for try to get assigned pe preset of a doctor with fake token with valid provider auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_get_assigned_pe_preset_of_an_doctor_with_algorithm_set_as_none_token(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, request_path=self.get_pe_preset_request_path,
                                                   token=pytest.configs.get_config('token_with_algorithm_set_as_none'))
        with allure.step('Proper error message should be returned for try to get assigned pe preset of a doctor with algorithm set as none token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_should_not_get_assigned_pe_preset_of_an_doctor_with_recently_blocked_auth_token(self):
        auth_token = RequestHandler.get_auth_token(user_name=self.user_name, password=self.password)
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, request_path=self.get_pe_preset_request_path,
                                                   token=auth_token)
        with allure.step('Proper error message should be returned for try to get assigned pe preset of a doctor with algorithm set as none token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_pe_preset_of_an_doctor(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, 
                                                   user_name=self.user_name,
                                                   password=self.password,
                                                   request_path=self.get_pe_preset_request_path, 
                                                   request_type="POST")
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 403
            assert response.reason == 'Forbidden'
            json_response = response.json()
            assert json_response['statusCode'] == 403
            assert json_response['error'] == 'Forbidden'
            assert json_response['message'] == "Permission denied."


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_pe_preset_of_an_doctor(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, 
                                                   user_name=self.user_name,
                                                   password=self.password,
                                                   request_path=self.get_pe_preset_request_path, 
                                                   request_type="PUT")
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 403
            assert response.reason == 'Forbidden'
            json_response = response.json()
            assert json_response['statusCode'] == 403
            assert json_response['error'] == 'Forbidden'
            assert json_response['message'] == "Permission denied."


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_pe_preset_of_an_doctor(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, 
                                                   user_name=self.user_name,
                                                   password=self.password,
                                                   request_path=self.get_pe_preset_request_path, 
                                                   request_type="PATCH")
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 404
            assert response.reason == 'Not Found'
            json_response = response.json()
            assert json_response['statusCode'] == 404
            assert json_response['error'] == 'Not Found'


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_pe_preset_of_an_doctor(self):
        response = RequestHandler.get_api_response(base_url=self.pe_preset_base_url, 
                                                   user_name=self.user_name,
                                                   password=self.password,
                                                   request_path=self.get_pe_preset_request_path, 
                                                   request_type="DELETE")
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 404
            assert response.reason == 'Not Found'
            json_response = response.json()
            assert json_response['statusCode'] == 404
            assert json_response['error'] == 'Not Found'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_apply_pe_preset(self):
        """
        Test for applying PE preset to a note using API.
        """
        # Prepare the API request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.note_id}&preset-id={self.provider_preset_id}'
        
        # Send the API request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url,
            token=TestPEPreset.auth_token,
            request_type='POST',
            request_path=apply_pe_preset_request_path)
        
        # Verify the response status and JSON data
        with allure.step('Proper datalist, status_code and reason should be returned for apply pe preset of a doctor'):
            assert response.status_code == 201
            assert response.reason == 'Created'
            json_response = response.json()

        # Compare the actual and expected JSON responses
        with open('resources/json_data/apply_pe_preset_response.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
            for item in expected_response:
                item["input"]["query"] = item["input"]["query"].replace("noteId: \"64dc422e-d388-446d-a565-19e3bff555c2\"", f"noteId: \"{self.note_id}\"")
            json_response_sorted = sorted(json.dumps(json_response, sort_keys=True)) 
            expected_response = sorted(json.dumps(expected_response, sort_keys=True))
            # Calculate the percentage similarity
            similarity = jsondiff.similarity(json_response_sorted, expected_response)
            assert similarity >= 0.9, "JSON files are not at least 90% similar"

        # Validate JSON schema of the response
        with open('resources/json_data/apply_pe_preset_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
            
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None



    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_api_should_responds_with_a_bad_request_error_when_invalid_provider_preset_id_is_provided(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.invalid_provider_preset_id}'
        
        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url,
            token=TestPEPreset.auth_token,
            request_type='POST',
            request_path=apply_pe_preset_request_path)
        
        # Verify response data
        with allure.step('Proper datalist, status_code and reason should be returned when invalid provider pe preset id is provided'):
            assert response.status_code == 400, f"Expected status code: 400, Actual: {response.status_code}"
            assert response.reason == 'Bad Request', f"Expected reason: Bad Request, Actual: {response.reason}"
            json_response = response.json()
            assert json_response['message'] == 'Error Reading Preset: 123456', f"Expected message: Error Reading Preset: 123456, Actual: {json_response['message']}"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_api_should_responds_with_a_bad_request_error_when_empty_provider_preset_id_is_provided(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id='
        
        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url,
            token=TestPEPreset.auth_token,
            request_type='POST',
            request_path=apply_pe_preset_request_path)
        
        # Verify response data
        with allure.step('Proper datalist, status_code and reason should be returned when empty provider pe preset id is provided'):
            assert response.status_code == 400, f"Expected status code: 400, Actual: {response.status_code}"
            assert response.reason == 'Bad Request', f"Expected reason: Bad Request, Actual: {response.reason}"
            json_response = response.json()
            assert json_response['message'] == 'Please provide noteId and PresetId', f"Expected message: Please provide noteId and PresetId, Actual: {json_response['message']}"
            

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_api_should_responds_with_a_bad_request_error_when_unassigned_preset_id_is_provided(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.unassigned_preset_id}'
        
        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url,
            token=TestPEPreset.auth_token,
            request_type='POST',
            request_path=apply_pe_preset_request_path)
        
        # Verify response data
        with allure.step('Proper datalist, status_code and reason should be returned when unassigned pe preset id is provided'):
            assert response.status_code == 400, f"Expected status code: 400, Actual: {response.status_code}"
            assert response.reason == 'Bad Request', f"Expected reason: Bad Request, Actual: {response.reason}"
            json_response = response.json()
            assert json_response['message'] == 'Error Reading Preset: 1529', f"Expected message: Error Reading Preset: 123456, Actual: {json_response['message']}"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_api_should_responds_with_a_bad_request_error_when_invalid_note_id_is_provided(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId=cbfffasd-2d92-4b0e-a5a9-5cc38c3b4748&preset-id={self.provider_preset_id}'
        
        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url,
            token=TestPEPreset.auth_token,
            request_type='POST',
            request_path=apply_pe_preset_request_path)
        
        # Verify response data
        with allure.step('Proper datalist, status_code and reason should be returned when invalid note id is provided'):
            assert response.status_code == 400, f"Expected status code: 400, Actual: {response.status_code}"
            assert response.reason == 'Bad Request', f"Expected reason: Bad Request, Actual: {response.reason}"
            json_response = response.json()
            assert json_response['message'] == 'Error Reading noteId: cbfffasd-2d92-4b0e-a5a9-5cc38c3b4748', f"Expected message: Error Reading noteId: cbfffasd-2d92-4b0e-a5a9-5cc38c3b4748, Actual: {json_response['message']}"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_api_should_responds_with_a_bad_request_error_when_empty_noteid_is_provided(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId=&preset-id={self.provider_preset_id}'
        
        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url,
            token=TestPEPreset.auth_token,
            request_type='POST',
            request_path=apply_pe_preset_request_path)
        
        # Verify response data
        with allure.step('Proper datalist, status_code and reason should be returned when empty noteid is provided'):
            assert response.status_code == 400, f"Expected status code: 400, Actual: {response.status_code}"
            assert response.reason == 'Bad Request', f"Expected reason: Bad Request, Actual: {response.reason}"
            json_response = response.json()
            assert json_response['message'] == 'Please provide noteId and PresetId', f"Expected message: Please provide noteId and PresetId, Actual: {json_response['message']}"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_should_not_apply_pe_preset_to_a_note_using_another_doctor_auth_token(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'
        
        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url,
            user_name=pytest.configs.get_config('lynx_enabled_rt_provider2'),
            password=self.password,
            request_type='POST',
            request_path=apply_pe_preset_request_path)
        
        # Verify response data
        with allure.step('Proper datalist, status_code and reason should be returned for try to apply pe preset to a note using another doctor auth token'):
            assert response.status_code == 401, f"Expected status code: 401, Actual: {response.status_code}"
            assert response.reason == 'Unauthorized', f"Expected reason: Unauthorized, Actual: {response.reason}"
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized', f"Expected message: Unauthorized, Actual: {json_response['message']}"

    
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_apply_pe_preset_to_a_note_of_an_doctor_with_invalid_auth_token(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            request_path=apply_pe_preset_request_path,
            token=pytest.configs.get_config('lynx_enabled_rt_provider_invalid_token'))
        
        # Verify response data
        with allure.step('Proper error message should be returned for try to apply pe preset to a note using invalid auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_apply_pe_preset_to_a_note_of_an_doctor_with_expired_auth_token(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            request_path=apply_pe_preset_request_path,
            token=pytest.configs.get_config('lynx_enabled_rt_provider_expired_token'))
        
        # Verify response data
        with allure.step('Proper error message should be returned for try to apply pe preset to a note of a doctor with expired auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_apply_pe_preset_to_a_note_of_an_doctor_with_fake_expired_date_auth_token(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            request_path=apply_pe_preset_request_path,
            token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_expired_date_token'))
        
        # Verify response data
        with allure.step('Proper error message should be returned for try to apply pe preset to a note of a doctor with fake expired date auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_apply_pe_preset_to_a_note_of_an_doctor_with_fake_token_with_valid_provider_token(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            request_path=apply_pe_preset_request_path,
            token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_token_with_valid_provider'))
        
        # Verify response data
        with allure.step('Proper error message should be returned for try to apply pe preset to a note of a doctor with fake token with valid provider auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_should_not_apply_pe_preset_to_a_note_of_an_doctor_with_algorithm_set_as_none_token(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            request_path=apply_pe_preset_request_path,
            token=pytest.configs.get_config('token_with_algorithm_set_as_none'))
        
        # Verify response data
        with allure.step('Proper error message should be returned for try to apply pe preset to a note of a doctor with algorithm set as none token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_should_not_apply_pe_preset_to_a_note_of_an_doctor_with_recently_blocked_auth_token(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        auth_token = RequestHandler.get_auth_token(user_name=self.user_name, password=self.password)
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        
        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            request_path=apply_pe_preset_request_path,
            token=auth_token)
        
        # Verify response data
        with allure.step('Proper error message should be returned for try to apply pe preset to a note of a doctor with recently blocked doctor'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_method_should_not_support_for_apply_pe_preset(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            user_name=self.user_name,
            password=self.password,
            request_path=apply_pe_preset_request_path, 
            request_type="GET")
        
        # Verify response data
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 403
            assert response.reason == 'Forbidden'
            json_response = response.json()
            assert json_response['statusCode'] == 403
            assert json_response['error'] == 'Forbidden'
            assert json_response['message'] == "Permission denied."


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_pe_preset_of_an_doctor(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            user_name=self.user_name,
            password=self.password,
            request_path=apply_pe_preset_request_path, 
            request_type="PUT")
        
        # Verify response data
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 403
            assert response.reason == 'Forbidden'
            json_response = response.json()
            assert json_response['statusCode'] == 403
            assert json_response['error'] == 'Forbidden'
            assert json_response['message'] == "Permission denied."


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_pe_preset_of_an_doctor(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            user_name=self.user_name,
            password=self.password,
            request_path=apply_pe_preset_request_path, 
            request_type="PATCH")
        
        # Verify response data
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 403
            assert response.reason == 'Forbidden'
            json_response = response.json()
            assert json_response['statusCode'] == 403
            assert json_response['error'] == 'Forbidden'
            assert json_response['message'] == "Permission denied."


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_pe_preset_of_an_doctor(self):
        # Construct the apply PE preset request path
        apply_pe_preset_request_path = f'api/applyPEPreset?noteId={TestPEPreset.noteId}&preset-id={self.provider_preset_id}'

        # Send the request and get the response
        response = RequestHandler.get_api_response(
            base_url=self.apply_pe_preset_base_url, 
            user_name=self.user_name,
            password=self.password,
            request_path=apply_pe_preset_request_path, 
            request_type="DELETE")
        
        # Verify response data
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 403
            assert response.reason == 'Forbidden'
            json_response = response.json()
            assert json_response['statusCode'] == 403
            assert json_response['error'] == 'Forbidden'
            assert json_response['message'] == "Permission denied."