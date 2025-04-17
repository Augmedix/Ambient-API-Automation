from urllib import response
import requests
import json
import pytest
from pages.appointment_api_page import AppointmentsApiPage

from pages.remote_state_graphql_page import RemoteStateGraphQLApiPage
from resources.data import Data
from testcases.base_test import BaseTest
from utils.api_request_data_handler import APIRequestDataHandler
from utils.dbConfig import DB
from utils.helper import get_formatted_date_str
from utils.request_handler import RequestHandler
import jwt
import allure
import jsondiff
import time


class TestRemoteStateGraphQL(BaseTest):
    remote_state_base_url = pytest.configs.get_config('graphql_base_url')
    appointment_id = ''
    headers = ''
    note_id = ''

    def setup_class(self):
        self.remote_state = RemoteStateGraphQLApiPage()
        self.data = Data()
        self.appointment = AppointmentsApiPage()
        self.db = DB()
        self.headers, user_guid, self.appointment_id, self.note_id = self.remote_state.post_transcript(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                                             password=pytest.configs.get_config("all_provider_password"))

        self.request_data = APIRequestDataHandler('remote_state_graphql')
        query_updated = self.data.get_note_complaints_selection_query.replace(self.data.noteIDPlaceholder,
                                                                 self.note_id)
        json_payload = self.request_data.get_modified_payload(query=query_updated)
        self.payload = json.dumps(json_payload, indent=4)

    def teardown_class(cls):
        cls.appointment.delete_appointment_note(appointment_id=cls.appointment_id, note_id=cls.note_id, headers=cls.headers)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_all_complaints_selections_with_lynx_enabled_user_token(self):
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=self.payload, headers=self.headers)
        with open('resources/json_data/complaints_selection.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
        with allure.step('Proper status_code, status_message and reason should be returned for valid user'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            json_response_sorted = sorted(json.dumps(json_response, sort_keys=True)) 
            expected_response = sorted(json.dumps(expected_response, sort_keys=True))
            # Calculate the percentage similarity
            similarity = jsondiff.similarity(json_response_sorted, expected_response)
            assert similarity >= 0.9, "JSON files are not at least 90% similar"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_error_message_should_be_shown_when_try_to_get_all_complaints_selections_with_lynx_disabled_user_token(self):
        lynx_disabled_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("rt_provider"),
                                                            password=pytest.configs.get_config("all_provider_password"))
        
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=self.payload, token=lynx_disabled_token)
        with allure.step('Proper create status_code, status_message and reason should be returned for lynx disabled user'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_get_complaints_selections_without_note_id_in_payload(self):
        query_updated = self.data.get_note_complaints_selection_query.replace(self.data.noteIDPlaceholder, "")
        json_payload = self.request_data.get_modified_payload(query=query_updated)
        payload = json.dumps(json_payload, indent=4)
        
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=payload, headers=self.headers)
        with allure.step('Proper create status_code, status_message and reason should be returned for without note id in payload'):
            assert response.status_code == 400
            assert response.reason == "Bad Request"
            json_response = response.json()
            assert json_response['data']['listComplaintsSelection'] == None
            assert json_response['errors'][0]['errorType'] == "DynamoDB:DynamoDbException"
            assert "One or more parameter values are not valid. The AttributeValue for a key attribute cannot contain an empty string value. Key: noteId (Service: DynamoDb, Status Code: 400, Request ID:" in json_response['errors'][0]['message']

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_get_complaints_selections_without_note_id_in_url(self):
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path="",
                                                request_type='POST', payload=self.payload, headers=self.headers)
        with allure.step('Proper create status_code, status_message and reason should be returned for without note id in url'):
            assert response.status_code == 404
            assert response.reason == "Not Found"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_get_complaints_selections_with_invalid_note_id_in_payload(self):
        query_updated = self.data.get_note_complaints_selection_query.replace(self.data.noteIDPlaceholder, "ajskhdksd")
        json_payload = self.request_data.get_modified_payload(query=query_updated)
        payload = json.dumps(json_payload, indent=4)
        
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=payload, headers=self.headers)
        with allure.step('Proper create status_code, status_message and reason should be returned for invalid note id in payload'):
            assert response.status_code == 400
            assert response.reason == "Bad Request"
            json_response = response.json()
            assert json_response['data']['listComplaintsSelection'] == None
            assert json_response['errors'][0]['errorType'] == "DynamoDB:DynamoDbException"
            assert "One or more parameter values are not valid. The AttributeValue for a key attribute cannot contain an invalid string value. Key: noteId (Service: DynamoDb, Status Code: 400, Request ID:" in json_response['errors'][0]['message']

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_get_complaints_selections_with_invalid_note_id_in_url(self):
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path="364sa",
                                                request_type='POST', payload=self.payload, headers=self.headers)
        with allure.step('Proper create status_code, status_message and reason should be returned for invalid note id in url'):
            assert response.status_code == 404
            assert response.reason == "Not Found"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_large_volume_requests(self):
        # Set the maximum response time in seconds
        max_response_time = 5

        # Set the number of requests to be sent
        num_requests = 100
        for i in range(num_requests):
            start_time = time.time()
            # Post a remote state graphql
            response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                    request_type='POST', payload=self.payload, headers=self.headers)
            end_time = time.time()
        with allure.step('Verify that the response time is within the acceptable range'):
            assert end_time - start_time < max_response_time, "Response time is too long!"
        with open('resources/json_data/complaints_selection.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
        with allure.step('Proper create status_code, status_message and reason should be returned for invalid note id in url'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            json_response_sorted = sorted(json.dumps(json_response, sort_keys=True)) 
            expected_response = sorted(json.dumps(expected_response, sort_keys=True))
            # Calculate the percentage similarity
            similarity = jsondiff.similarity(json_response_sorted, expected_response)
            assert similarity >= 0.8, "JSON files are not at least 80% similar"
    
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_graphql_data_should_not_possible_with_lynx_enabled_rt_provider_invalid_token(self):
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=self.payload, token=pytest.configs.get_config("lynx_enabled_rt_provider_invalid_token"))
        with allure.step('Proper create status_code, status_message and reason should be returned for invalid token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_graphql_data_should_not_possible_with_lynx_enabled_rt_provider_expired_token(self):
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=self.payload, token=pytest.configs.get_config("lynx_enabled_rt_provider_expired_token"))
        with allure.step('Proper create status_code, status_message and reason should be returned for expired token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"

    
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_graphql_data_should_not_possible_with_algorithm_set_as_none_token(self):
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=self.payload, token=pytest.configs.get_config("token_with_algorithm_set_as_none"))
        with allure.step('Proper create status_code, status_message and reason should be returned '):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"


    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_post_graphql_data_should_not_possible_with_lynx_enabled_rt_provider_blocked_token(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=self.payload, headers=self.headers)
        with allure.step('Proper create status_code, status_message and reason should be returned for blocked token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_graphql_data_should_not_possible_with_fake_token_created_with_valid_provider(self):
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=self.payload, token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_token_with_valid_provider'))
        with allure.step('Proper create status_code, status_message and reason should be returned for fake token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_graphql_data_should_not_possible_with_fake_token_created_with_expiration_date_updated(self):
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=self.payload, token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_expired_date_token'))
        with allure.step('Proper create status_code, status_message and reason should be returned for fake expired token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_graphql_data_with_different_noteID_valid_from_same_doctor_appointments_on_url_with_valid_note_id_in_the_payload(self):
        # Create and authorize another Note for same doctor 
        headers, user_guid, appointment_id, note_id = self.remote_state.post_transcript(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                                             password=pytest.configs.get_config("all_provider_password"))
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=note_id,
                                                request_type='POST', payload=self.payload, headers=headers)
        # Delete note
        self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)
        with allure.step('Proper create status_code, status_message and reason should be returned for different noteID valid from same doctor appointments on url with valid note id in the payload'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            assert json_response['data']['getNote'] == None
            assert json_response['errors'][0]['errorType'] == "Unauthorized"
            assert json_response['errors'][0]['message'] == "Not Authorized to access getNote on type Note"
            #TODO- Proper Assertion will be added after get the final api

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_graphql_data_with_valid_noteId_from_same_doctor_appointments_on_url_with_different_valid_note_id_in_the_payload(self):
        # Create and authorize another Note for same doctor 
        headers, user_guid, appointment_id, note_id = self.remote_state.post_transcript(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                                             password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('remote_state_graphql')
        query_updated = self.data.get_note_query.replace(self.data.noteIDPlaceholder,note_id)
        json_payload = request_data.get_modified_payload(query=query_updated)
        payload = json.dumps(json_payload, indent=4)
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=payload, headers=headers)
        # Delete note
        self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)
        with allure.step('Proper create status_code, status_message and reason should be returned for different noteID valid from same doctor appointments on url with valid note id in the payload'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            assert json_response['data']['getNote'] == None
            assert json_response['errors'][0]['errorType'] == "Unauthorized"
            assert json_response['errors'][0]['message'] == "Not Authorized to access getNote on type Note"
            #TODO- Proper Assertion will be added after get the final api

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_graphql_data_with_different_noteID_valid_from_different_doctor_appointments_on_url_with_valid_note_id_of_same_doctor_in_the_payload(self):
        # Create and authorize another Note for different doctor
        headers, user_guid, appointment_id, note_id = self.remote_state.post_transcript(user_name=pytest.configs.get_config("lynx_enabled_rt_provider2"),
                                                                             password=pytest.configs.get_config("all_provider_password"))
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=note_id,
                                                request_type='POST', payload=self.payload, headers=self.headers)
        # Delete note
        self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)
        with allure.step('Proper create status_code, status_message and reason should be returned for different noteID valid from same doctor appointments on url with valid note id in the payload'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_graphql_data_with_valid__noteId_of_same_doctor_on_url_with_valid_note_id_from_different_doctor_in_the_payload(self):
        # Create and authorize another Note for same doctor 
        headers, user_guid, appointment_id, note_id = self.remote_state.post_transcript(user_name=pytest.configs.get_config("lynx_enabled_rt_provider2"),
                                                                             password=pytest.configs.get_config("all_provider_password"))
        request_data = APIRequestDataHandler('remote_state_graphql')
        query_updated = self.data.get_note_query.replace(self.data.noteIDPlaceholder,
                                                                 note_id)
        json_payload = request_data.get_modified_payload(query=query_updated)
        payload = json.dumps(json_payload, indent=4)
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                request_type='POST', payload=payload, headers=headers)
        # Delete note
        self.appointment.delete_appointment_note(appointment_id=appointment_id, note_id=note_id, headers=headers)
        with allure.step('Proper create status_code, status_message and reason should be returned for different noteID valid from same doctor appointments on url with valid note id from different doctor in the payload'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_method_should_not_support_for_post_graphql_data_endpoint(self):
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                   payload=self.payload, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'GET' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_post_graphql_data_endpoint(self):
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                   request_type='PUT',
                                                   payload=self.payload, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_post_graphql_data_endpoint(self):
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                   request_type='PATCH',
                                                   payload=self.payload, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_post_graphql_data_endpoint(self):
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=self.note_id,
                                                   request_type='DELETE',
                                                   payload=self.payload, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_post_graphql_data_should_not_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2")
        headers, user_guid, appointment_id, note_id = self.remote_state.post_transcript(user_name=self.user_name,
                                                                                        password=pytest.configs.get_config("all_provider_password"))

        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.remote_state.reset_password(headers=headers, new_password='@ugmed1X@1')
        # Post a remote state graphql
        response = RequestHandler.get_api_response(base_url=self.remote_state_base_url, request_path=note_id,
                                                request_type='POST', payload=self.payload, headers=headers)
        with allure.step('Proper create status_code, status_message and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
            json_response = response.json()
            assert json_response['message'] == "Unauthorized"
