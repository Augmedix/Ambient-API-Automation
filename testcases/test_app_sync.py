from urllib import response

import jsondiff
import requests
import json
import pytest
from pages.appointment_api_page import AppointmentsApiPage
from pages.app_sync_api_page import AppSyncApiPage
from pages.remote_state_graphql_page import RemoteStateGraphQLApiPage
from resources.data import Data
from testcases.base_test import BaseTest
from utils.api_request_data_handler import APIRequestDataHandler
from utils.dbConfig import DB
from utils.helper import get_formatted_date_str
from utils.request_handler import RequestHandler
import jwt
import allure
import re
import jsonschema
from jsonschema.validators import  validate, Draft7Validator, create


class TestAppSync(BaseTest):
    app_sync_base_url = pytest.configs.get_config('graphql_base_url')
    request_data = APIRequestDataHandler('app_sync')
    appointment_id = ''
    headers = ''
    note_id = ''
    app_sync_path = ''

    def setup_class(self):
        self.remote_state = RemoteStateGraphQLApiPage()
        self.app_sync = AppSyncApiPage()
        self.data = Data()
        self.appointment = AppointmentsApiPage()
        self.db = DB()
        headers, user_guid, appointment_id, note_id = self.remote_state.post_transcript(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                                             password=pytest.configs.get_config("all_provider_password"))
        self.headers = headers
        self.note_id = note_id
        self.appointment_id = appointment_id
        self.app_sync_path = self.note_id
        query_updated = self.data.get_note_complaints_selection_query.replace(self.data.noteIDPlaceholder,
                                                                 self.note_id)
        json_payload = self.request_data.get_modified_payload(query=query_updated)
        self.payload = json.dumps(json_payload, indent=4)

    def teardown_class(cls):
        cls.appointment.delete_appointment_note(appointment_id=cls.appointment_id, note_id=cls.note_id, headers=cls.headers)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_all_complaints_selection_of_a_note_for_valid_lynx_enabled_rt_token(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="POST", payload=self.payload, headers=self.headers)
        with open('resources/json_data/app_sync_response.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            json_response = response_body.json()
            # Calculate the percentage similarity
            similarity = jsondiff.similarity(json_response, expected_response)
            assert similarity >= 0.90, "JSON files are not at least 90% similar"
            # assert json_response == expected_response
        with open('resources/json_data/app_sync_response_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None
                

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_lynx_disabled_user_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))

        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="POST", payload=self.payload, token=lynx_disabled_token)
        with allure.step('Proper status_code, status_message and reason should be returned for lynx disabled user token'):
            assert response_body.status_code == 401
            assert response_body.reason == "Unauthorized"
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_lynx_enabled_rt_provider_invalid_token(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="POST", payload=self.payload, token=pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token"))
        with allure.step('Proper status_code, status_message and reason should be returned for invalid token'):
            assert response_body.status_code == 401
            assert response_body.reason == "Unauthorized"
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_lynx_enabled_rt_provider_expired_token(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="POST", payload=self.payload, token=pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token"))
        with allure.step('Proper status_code, status_message and reason should be returned for expired token'):
            assert response_body.status_code == 401
            assert response_body.reason == "Unauthorized"
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_algorithm_set_as_none_token(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="POST", payload=self.payload, token=pytest.configs.get_config("token_with_algorithm_set_as_none"))
        with allure.step('Proper status_code, status_message and reason should be returned for algorithm set as none token'):
            assert response_body.status_code == 401
            assert response_body.reason == "Unauthorized"
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_fake_token_created_with_valid_provider(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="POST", payload=self.payload, token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_token_with_valid_provider'))
        with allure.step('Proper status_code, status_message and reason should be returned for fake token created with valid provider'):
            assert response_body.status_code == 401
            assert response_body.reason == "Unauthorized"
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_fake_token_created_with_expiration_date_updated(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="POST", payload=self.payload, token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_expired_date_token'))
        with allure.step('Proper status_code, status_message and reason should be returned for fake token created with expiration date updated'):
            assert response_body.status_code == 401
            assert response_body.reason == "Unauthorized"
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_different_noteID_valid_from_same_doctor_on_url_and_in_the_payload(self):
        # Create another Note for same doctor 
        headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date,\
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                password=pytest.configs.get_config("all_provider_password"))
        
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=note_id,
                                                        request_type="POST", payload=self.payload, headers=headers)
        # Delete note
        self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)
        with allure.step('Proper status_code, status_message and reason should be returned for different noteID valid from same doctor appointments on url with valid note id in the payload'):
            assert response_body.status_code == 404
            assert response_body.reason == "Not Found"
            # TODO: Proper assertion need to add after proper error logic implemented

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_without_noteID_in_the_payload(self):
        query_updated = self.data.get_note_complaints_selection_query.replace(self.data.noteIDPlaceholder,
                                                                 "")
        json_payload = self.request_data.get_modified_payload(query=query_updated)
        payload = json.dumps(json_payload, indent=4)
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.note_id,
                                                request_type='POST', payload=payload, headers=self.headers)
        with allure.step('Proper status_code, status_message and reason should be returned for without note id in the payload'):
            assert response_body.status_code == 400
            assert response_body.reason == "Bad Request"
            json_response = response_body.json()
            assert json_response['data']['listComplaintsSelection'] == None
            assert json_response['errors'][0]['data'] == None
            assert json_response['errors'][0]['errorType'] == "DynamoDB:DynamoDbException"
            assert "One or more parameter values are not valid. The AttributeValue for a key attribute cannot contain an empty string value. Key: noteId (Service: DynamoDb, Status Code: 400, Request ID:" in json_response['errors'][0]['message']


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_without_noteID_in_the_url(self):
        response = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path="",
                                                request_type='POST', payload=self.payload, headers=self.headers)
        with allure.step('Proper status_code, status_message and reason should be returned for without note id in the payload'):
            assert response.status_code == 500
            assert response.reason == 'Internal Server Error'
            json_response = response.json()
            assert json_response['message'] == 'Internal Server Error'
    
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_app_sync_api_should_returned_not_found_error_to_get_complaints_selection_data_of_a_note_with_invalid_noteID_in_the_payload(self):
        query_updated = self.data.get_note_complaints_selection_query.replace(self.data.noteIDPlaceholder,
                                                                    "fgshjdgfshjgfjhgf")
        json_payload = self.request_data.get_modified_payload(query=query_updated)
        payload = json.dumps(json_payload, indent=4)
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.note_id,
                                                request_type='POST', payload=payload, headers=self.headers)
        with allure.step('Proper status_code, status_message and reason should be returned for invalid note id in the payload'):
            assert response_body.status_code == 404
            assert response_body.reason == "Not Found"
             # TODO: Proper assertion need to add after proper error logic implemented

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_app_sync_api_should_returned_error_to_get_complaints_selection_data_of_a_note_with_invalid_noteID_in_the_url(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path="gfhgsgsdjfgs",
                                                request_type='POST', payload=self.payload, headers=self.headers)
        with allure.step('Proper status_code, status_message and reason should be returned for invalid note id in the payload'):
            assert response_body.status_code == 500
            assert response_body.reason == 'Internal Server Error'
            # TODO: Proper assertion need to add after proper error logic implemented

    

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_valid_noteID_from_different_doctor_on_url_with_valid_note_id_of_same_doctor_in_the_payload(self):
        # Create another Note for different doctor 
        headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date,\
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider2"),
                                                password=pytest.configs.get_config("all_provider_password"))
        
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=note_id,
                                                        request_type="POST", payload=self.payload, headers=self.headers)
        # Delete note
        self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)
        with allure.step('Proper status_code, status_message and reason should be returned for valid noteID from different doctor on url with valid note id of same doctor in the payload'):
            assert response_body.status_code == 401
            assert response_body.reason == "Unauthorized"
            json_response = response_body.json()
            assert json_response['message'] == "Unauthorized"


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_valid_noteID_from_same_doctor_on_url_with_valid_note_id_of_different_doctor_in_the_payload(self):
        # Create another Note for different doctor 
        headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date,\
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=pytest.configs.get_config("lynx_enabled_rt_provider2"),
                                                password=pytest.configs.get_config("all_provider_password"))
        
        query_updated = self.data.get_note_complaints_selection_query.replace(self.data.noteIDPlaceholder,
                                                                 note_id)
        json_payload = self.request_data.get_modified_payload(query=query_updated)
        payload = json.dumps(json_payload, indent=4)
        
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.note_id,
                                                        request_type="POST", payload=payload, headers=self.headers)
        # Delete note
        self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)
        with allure.step('Proper status_code, status_message and reason should be returned for valid noteID from same doctor on url with valid note id of different doctor in the payload'):
            assert response_body.status_code == 404
            assert response_body.reason == "Not Found"
            # TODO: Proper assertion need to add after proper error logic implemented


    """ @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security1
    def test_app_sync_api_should_not_get_complaints_selection_data_of_a_note_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        headers, token, user_guid, response_body, appointment_id, patient_id, note_status, creation_date, service_date,\
        expiration_date, note_id = self.appointment.create_and_get_appointment_note_info(
                                                user_name=self.user_name,
                                                password=pytest.configs.get_config("all_provider_password"))

        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.app_sync.reset_password(headers=headers, new_password='@ugmed1X@1')
        query_updated = self.data.get_note_organize_selection_query.replace(self.data.noteIDPlaceholder,
                                                                 note_id)
        json_payload = self.request_data.get_modified_payload(query=query_updated)
        payload = json.dumps(json_payload, indent=4)
        response = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=note_id,
                                                request_type='POST', payload=payload, headers=headers)
        with allure.step('Proper status_code, status_message and reason should be returned changed password previous token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized" """

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.negative
    def test_get_method_should_not_supported_get_all_complaints_selection_of_a_note_for_valid_lynx_enabled_rt_token(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="GET", payload=self.payload, headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 503
            assert response_body.reason == 'Service Unavailable'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.negative
    def test_delete_method_should_not_supported_get_all_complaints_selection_of_a_note_for_valid_lynx_enabled_rt_token(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="DELETE", payload=self.payload, headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 503
            assert response_body.reason == 'Service Unavailable'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.negative
    def test_put_method_should_not_supported_get_all_complaints_selection_of_a_note_for_valid_lynx_enabled_rt_token(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="PUT", payload=self.payload, headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 503
            assert response_body.reason == 'Service Unavailable'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.negative
    def test_patch_method_should_not_supported_get_all_complaints_selection_of_a_note_for_valid_lynx_enabled_rt_token(self):
        response_body = RequestHandler.get_api_response(base_url=self.app_sync_base_url, request_path=self.app_sync_path,
                                                        request_type="PATCH", payload=self.payload, headers=self.headers)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 503
            assert response_body.reason == 'Service Unavailable'
            





    