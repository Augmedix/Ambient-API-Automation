from urllib import response
import requests
import json
import pytest

from pages.authorization_api_page import AuthorizationApiPage
from resources.data import Data
from testcases.base_test import BaseTest
from utils.api_request_data_handler import APIRequestDataHandler
from utils.dbConfig import DB
from utils.helper import get_formatted_date_str
from utils.request_handler import RequestHandler
import jwt
import allure
import uuid
from jsonschema.validators import  validate


class TestAuthorizationService(BaseTest):
    base_url = pytest.configs.get_config('authorization_base_url')
    resource_id = ''
    headers = ''

    def setup_class(self):
        self.authorization = AuthorizationApiPage()
        self.data = APIRequestDataHandler('authorization')
        self.authorize_resource_expected_schema = json.loads(json.dumps(self.data.get_modified_payload(name="authorize_resource_schema")))
        self.ehr_lynx_enabled_rt_provider_token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'), password=pytest.configs.get_config('all_provider_password'))
        token_decoded = jwt.decode(self.ehr_lynx_enabled_rt_provider_token, options={"verify_signature": False})
        self.ehr_lynx_enabled_rt_provider_guid = token_decoded["guid"]
    # @pytest.fixture(autouse=True)
    # def setup_testcase(self):
    #     yield

    def teardown_method(self):
        if self.resource_id:
            self.authorization.delete_resource(self.resource_id, self.headers)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_create_resource_with_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))
        with allure.step('Proper create status_code and reason should be returned for valid user'):
            assert response.status_code == 201
            assert response.reason == "Created"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_resource_cannot_be_possible_with_lynx_disabled_user_token(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        with allure.step('Proper status_code and reason should be returned for invalid user'):
            assert response.status_code == 400
            assert response.reason == "Bad Request"
            json_response = response.json()
            assert json_response["timestamp"]
            assert json_response["status"] == 400
            assert json_response["error"] == "Bad Request"
            assert json_response["message"] == "No GUID found in the request."
            assert json_response["path"] == "/authorize"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_resource_cannot_be_possible_with_expired_lynx_enabled_user_token(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                                        auth_token=pytest.configs.get_config('lynx_enabled_rt_provider_expired_token'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_resource_cannot_be_possible_with_invalid_lynx_enabled_user_token(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                                        auth_token=pytest.configs.get_config('lynx_enabled_rt_provider_invalid_token'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_resource_cannot_be_possible_with_algorithm_set_as_none_token(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                                        auth_token=pytest.configs.get_config('token_with_algorithm_set_as_none'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_create_resource_cannot_be_possible_with_blocked_lynx_enabled_user_token(self):
        self.user_name = pytest.configs.get_config('lynx_enabled_rt_provider')
        user_token = RequestHandler.get_auth_token(user_name=self.user_name,
                                                   password=pytest.configs.get_config('all_provider_password'))

        # self.authorization.blocked_user(pytest.configs.get_config('lynx_enabled_nrt_provider'))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')

        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                        auth_token=user_token)
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_authorize_resource_for_valid_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=self.headers)
        with allure.step('Proper status_code, reason and response data should be returned for authorize user'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            assert json_response['resourceId'] == self.resource_id
            assert json_response['userId'] == user_guid
            assert json_response['creationDate'].startswith(get_formatted_date_str(_date_format='%Y-%m-%d'))
        with allure.step('json schema is validated'):
            assert validate(json_response, self.authorize_resource_expected_schema) is None

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_unauthorized_resource_cannot_be_possible_with_valid_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'))
        with allure.step('Proper status_code, reason and response data should be returned unauthorized user'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_authorize_resource_cannot_be_possible_with_expired_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url,
                                                   request_path=resource_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_expired_token'))
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_authorize_resource_cannot_be_possible_with_algorithm_set_as_none_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url,
                                                   request_path=resource_path,
                                                   token=pytest.configs.get_config('token_with_algorithm_set_as_none'))
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_authorize_resource_cannot_be_possible_with_invalid_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url,
                                                   request_path=resource_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_invalid_token'))
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_get_authorize_resource_cannot_be_possible_with_blocked_lynx_enabled_user_token(self):
        self.user_name = pytest.configs.get_config('lynx_enabled_rt_provider')
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config('all_provider_password'))
        # self.authorization.blocked_user(pytest.configs.get_config('lynx_enabled_nrt_provider'))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url,
                                                   request_path=resource_path, headers=self.headers)
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
        # self.authorization.update_user_status(key_value=pytest.configs.get_config('lynx_enabled_nrt_provider'))

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_authorize_resource_cannot_be_possible_with_lynx_disabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url,
                                                   request_path=resource_path,
                                                   user_name=pytest.configs.get_config('rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'))
        with allure.step('Proper status_code and reason should be returned for invalid user'):
            assert response.status_code == 400
            assert response.reason == "Bad Request"
            json_response = response.json()
            assert json_response["timestamp"]
            assert json_response["status"] == 400
            assert json_response["error"] == "Bad Request"
            assert json_response["message"] == "No GUID found in the request."
            assert json_response["path"] == f'/authorize/{self.resource_id}'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_authorize_resource_cannot_be_possible_with_expired_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE',
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_expired_token'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_authorize_resource_cannot_be_possible_with_algorithm_set_as_none_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE',
                                                   token=pytest.configs.get_config('token_with_algorithm_set_as_none'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_authorize_resource_cannot_be_possible_with_invalid_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE',
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_invalid_token'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_delete_authorize_resource_cannot_be_possible_with_blocked_lynx_enabled_user_token(self):
        self.user_name = pytest.configs.get_config('lynx_enabled_rt_provider')
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config('all_provider_password'))

        # self.authorization.blocked_user(pytest.configs.get_config('lynx_enabled_nrt_provider'))
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE', headers=self.headers)
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"
        # self.authorization.update_user_status(key_value=pytest.configs.get_config('lynx_enabled_nrt_provider'))

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_authorize_resource_cannot_be_possible_with_lynx_disabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE',
                                                   user_name=pytest.configs.get_config('rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'))

        with allure.step('Proper status_code and reason should be returned for invalid user'):
            assert response.status_code == 400
            assert response.reason == "Bad Request"
            json_response = response.json()
            assert json_response["timestamp"]
            assert json_response["status"] == 400
            assert json_response["error"] == "Bad Request"
            assert json_response["message"] == "No GUID found in the request."
            assert json_response["path"] == f'/authorize/{self.resource_id}'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_delete_authorize_resource_can_be_possible_with_valid_lynx_enabled_user_token(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))
        resource_path = f'authorize/{resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE', headers=headers)
        with allure.step('Proper status_code and reason should be returned'):
            assert response.status_code == 204
            assert response.reason == "No Content"

        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=headers)
        with allure.step('Proper status_code, reason and response data should be returned for trying get deleted resource,'):
            assert response.status_code == 404
            assert response.reason == "Not Found"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == 'Resource not found'
            assert json_response['path'] == f'/authorize/{resource_id}'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_unauthorized_resource_cannot_be_possible_with_valid_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url,request_path=resource_path,
                                                   request_type='DELETE',
                                                   user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'))
        with allure.step('Proper status_code and reason should be returned'):
            assert response.status_code == 404
            assert response.reason == "Not Found"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == 'Resource not found'
            assert json_response['path'] == f'/authorize/{self.resource_id}'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_resource_cannot_be_possible_with_fake_expired_date_lynx_enabled_user_token(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                    auth_token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_expired_date_token'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_authorize_resource_cannot_be_possible_with_fake_expired_date_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url,
                                                   request_path=resource_path,
                                                   token=pytest.configs.get_config(
                                                       'lynx_enabled_rt_provider_fake_expired_date_token'))
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_authorize_resource_cannot_be_possible_with_fake_expired_date_lynx_enabled_user_token(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE',
                                                   token=pytest.configs.get_config(
                                                       'lynx_enabled_rt_provider_fake_expired_date_token'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_resource_cannot_be_possible_for_fake_token_with_valid_provider(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                    auth_token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_token_with_valid_provider'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_authorize_resource_cannot_be_possible_for_fake_token_with_valid_provider(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url,
                                                   request_path=resource_path,
                                                   token=pytest.configs.get_config(
                                                       'lynx_enabled_rt_provider_fake_token_with_valid_provider'))
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_delete_authorize_resource_cannot_be_possible_for_fake_token_with_valid_provider(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE',
                                                   token=pytest.configs.get_config(
                                                       'lynx_enabled_rt_provider_fake_token_with_valid_provider'))

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_method_should_not_support_for_create_resource_endpoint(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'),
                                                        request_type='GET')
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'GET' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_create_resource_endpoint(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'),
                                                        request_type='PUT')
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_create_resource_endpoint(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'),
                                                        request_type='PATCH')
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_create_resource_endpoint(self):
        response, headers, user_guid, resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'),
                                                        request_type='DELETE')
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_authorize_resource_endpoint(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_type='PUT', request_path=resource_path, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_authorize_resource_endpoint(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_type='POST', request_path=resource_path, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_authorize_resource_endpoint(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_type='PATCH', request_path=resource_path, headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_create_resource_cannot_be_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_rt_provider2')
        user_token = RequestHandler.get_auth_token(user_name=self.user_name,
                                                   password=pytest.configs.get_config('all_provider_password'))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.authorization.reset_password(token=user_token, new_password='@ugmed1X@1')
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(auth_token=user_token)

        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_get_authorize_resource_cannot_be_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_rt_provider2')
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config('all_provider_password'))

        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.authorization.reset_password(headers=self.headers, new_password='@ugmed1X@1')

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url,
                                                   request_path=resource_path, headers=self.headers)
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_delete_authorize_resource_cannot_be_possible_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_rt_provider2')
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        user_name=self.user_name,
                                                        password=pytest.configs.get_config('all_provider_password'))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.authorization.reset_password(headers=self.headers, new_password='@ugmed1X@1')

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE', headers=self.headers)
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_create_authorize_resource_with_empty_request_body(self):
        headers = self.data.get_modified_headers(Authorization=f'Bearer {self.ehr_lynx_enabled_rt_provider_token}')
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path='authorize',
                                                   request_type='POST', payload='', headers=headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 400
            assert response.reason == "Bad Request"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 400
            assert json_response['error'] == 'Bad Request'
            assert "Required request body is missing" in json_response['message']
            assert json_response['path'] == f'/authorize'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_create_authorize_resource_with_empty_array_in_request_body(self):
        headers = self.data.get_modified_headers(Authorization=f'Bearer {self.ehr_lynx_enabled_rt_provider_token}')
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path='authorize',
                                                   request_type='POST', payload='[]', headers=headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 400
            assert response.reason == "Bad Request"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == "400"
            assert json_response['error'] == 'Bad Request'
            assert "Resource list cannot be empty" in json_response['message']

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_create_authorize_resource_with_invalid_key_in_request_body(self):
        payload = '[{"resourceid": "a5a65f21-af85-49c5-a5cd-b71ae3bfdc59"}]'
        headers = self.data.get_modified_headers(Authorization=f'Bearer {self.ehr_lynx_enabled_rt_provider_token}')
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path='authorize',
                                                   request_type='POST', payload=payload, headers=headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 500
            assert response.reason == "Internal Server Error"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert json_response['message'] == 'Failed to process request.'
            assert json_response['path'] == f'/authorize'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_create_authorize_resource_with_empty_resourceId_key_value_in_request_body(self):
        self.resource_id = ""
        payload = '[{"resourceId": ""}]'
        self.headers = self.data.get_modified_headers(Authorization=f'Bearer {self.ehr_lynx_enabled_rt_provider_token}')
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path='authorize',
                                                   request_type='POST', payload=payload, headers=self.headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 500
            assert response.reason == "Internal Server Error"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert json_response['message'] == 'Failed to process request.'
            assert json_response['path'] == f'/authorize'


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_create_authorize_resource_with_invalid_resourceId_key_value_in_request_body(self):
        self.resource_id="or 1=1;--"
        payload = '[{"resourceId": "or 1=1;--"}]'
        self.headers = self.data.get_modified_headers(Authorization=f'Bearer {self.ehr_lynx_enabled_rt_provider_token}')
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path='authorize',
                                                   request_type='POST', payload=payload, headers=self.headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 400
            assert response.reason == "Bad Request"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == "400"
            assert json_response['error'] == 'Bad Request'
            assert "ResourceId must be of 32 to 52 length with no special characters." in json_response['message']

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_create_multiple_authorize_resource_with_valid_multiple_resourceId_in_request_body(self):
        payload = '[{"resourceId": "a5a65f21-af85-49c5-a5cd-b71ae3bfdc59"},{"resourceId": "a5a65f21-af85-49c5-a5cd-b71ae3bfdc60"}]'
        headers = self.data.get_modified_headers(Authorization=f'Bearer {self.ehr_lynx_enabled_rt_provider_token}')
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path='authorize',
                                                   request_type='POST', payload=payload, headers=headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 201
            assert response.reason == "Created"
        self.authorization.delete_resource("a5a65f21-af85-49c5-a5cd-b71ae3bfdc59", headers)
        self.authorization.delete_resource("a5a65f21-af85-49c5-a5cd-b71ae3bfdc60", headers)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_get_authorize_resource_without_resourceId_in_request_path(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        auth_token=self.ehr_lynx_enabled_rt_provider_token)

        resource_path = f'authorize/'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=self.headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 405
            assert response.reason == "Method Not Allowed"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'GET' not supported"
            assert json_response['path'] == f'/authorize'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_get_authorize_resource_using_resourceId_as_query_params(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        auth_token=self.ehr_lynx_enabled_rt_provider_token)

        resource_path = f'authorize?resourceId={self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=self.headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 405
            assert response.reason == "Method Not Allowed"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'GET' not supported"
            assert json_response['path'] == f'/authorize'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_get_resource_using_invalid_resourceId_in_request_path(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        auth_token=self.ehr_lynx_enabled_rt_provider_token)

        resource_path = f'authorize/{self.resource_id}ab-'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=self.headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 404
            assert response.reason == "Not Found"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == "Resource not found"
            assert json_response['path'] == f'/authorize/{self.resource_id}ab-'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_delete_authorize_resource_without_resourceId_in_request_path(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        auth_token=self.ehr_lynx_enabled_rt_provider_token)

        resource_path = f'authorize/'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, request_type='DELETE', headers=self.headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 405
            assert response.reason == "Method Not Allowed"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"
            assert json_response['path'] == f'/authorize'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_delete_authorize_resource_using_resourceId_as_query_params(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        auth_token=self.ehr_lynx_enabled_rt_provider_token)

        resource_path = f'authorize?resourceId={self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, request_type='DELETE', headers=self.headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 405
            assert response.reason == "Method Not Allowed"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"
            assert json_response['path'] == f'/authorize'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_should_be_shown_when_try_to_delete_resource_using_invalid_resourceId_in_request_path(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(
                                                        auth_token=self.ehr_lynx_enabled_rt_provider_token)

        resource_path = f'authorize/{self.resource_id}ab-'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, request_type='DELETE', headers=self.headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 404
            assert response.reason == "Not Found"
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == "Resource not found"
            assert json_response['path'] == f'/authorize/{self.resource_id}ab-'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_create_get_delete_flows_for_multiple_resource(self):
        payload = '[{"resourceId": "a5a65f21-af85-49c5-a5cd-b71ae3bfdc44"},{"resourceId": "a5a65f21-af85-49c5-a5cd-b71ae3bfdc55"}]'
        headers = self.data.get_modified_headers(Authorization=f'Bearer {self.ehr_lynx_enabled_rt_provider_token}')
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path='authorize',
                                                   request_type='POST', payload=payload, headers=headers)
        with allure.step('Proper status_code, reason and response data should be returned for create multiple resource'):
            assert response.status_code == 201
            assert response.reason == "Created"

        resource_path = f'authorize/a5a65f21-af85-49c5-a5cd-b71ae3bfdc44'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=headers)
        with allure.step('Proper status_code, reason and response data should be returned to get created authorized resource'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            assert json_response['resourceId'] == 'a5a65f21-af85-49c5-a5cd-b71ae3bfdc44'
            assert json_response['userId'] == self.ehr_lynx_enabled_rt_provider_guid
            assert json_response['creationDate'].startswith(get_formatted_date_str(_date_format='%Y-%m-%d'))
        resource_path = f'authorize/a5a65f21-af85-49c5-a5cd-b71ae3bfdc55'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=headers)
        with allure.step('Proper status_code, reason and response data should be returned to get created authorized resource'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            assert json_response['resourceId'] == 'a5a65f21-af85-49c5-a5cd-b71ae3bfdc55'
            assert json_response['userId'] == self.ehr_lynx_enabled_rt_provider_guid
            assert json_response['creationDate'].startswith(get_formatted_date_str(_date_format='%Y-%m-%d'))

        resource_path = f'authorize/a5a65f21-af85-49c5-a5cd-b71ae3bfdc44'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, request_type='DELETE', headers=headers)
        with allure.step('Proper status_code, reason and response data should returned to delete authorized resource'):
            assert response.status_code == 204
            assert response.reason == "No Content"
            response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=headers)
            assert response.status_code == 404
            assert response.reason == "Not Found"

        resource_path = f'authorize/a5a65f21-af85-49c5-a5cd-b71ae3bfdc55'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                   request_type='DELETE', headers=headers)
        with allure.step('Proper status_code, reason and response data should returned to delete authorized resource'):
            assert response.status_code == 204
            assert response.reason == "No Content"
            response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path,
                                                       headers=headers)
            assert response.status_code == 404
            assert response.reason == "Not Found"

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_similar_resourceId_for_multiple_user_resource_does_not_cross_match(self):
        response, self.headers, user_guid, self.resource_id = self.authorization.create_resource(user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                        password=pytest.configs.get_config('all_provider_password'))

        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 201
            assert response.reason == "Created"

        payload = '[{"resourceId": "' + self.resource_id + '"}]'
        headers = self.data.get_modified_headers(Authorization=f'Bearer {self.ehr_lynx_enabled_rt_provider_token}')
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path='authorize',
                                                   request_type='POST', payload=payload, headers=headers)
        with allure.step('Proper status_code, reason and response data should be returned'):
            assert response.status_code == 201
            assert response.reason == "Created"

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=self.headers)
        with allure.step(
                'Proper status_code, reason and response data should be returned to get created authorized resource'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            assert json_response['resourceId'] == self.resource_id
            assert json_response['userId'] == user_guid
            assert json_response['creationDate'].startswith(get_formatted_date_str(_date_format='%Y-%m-%d'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=headers)
        with allure.step(
                'Proper status_code, reason and response data should be returned to get created authorized resource'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            assert json_response['resourceId'] == self.resource_id
            assert json_response['userId'] == self.ehr_lynx_enabled_rt_provider_guid
            assert json_response['creationDate'].startswith(get_formatted_date_str(_date_format='%Y-%m-%d'))

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, request_type='DELETE', headers=headers)
        with allure.step('Proper status_code, reason and response data should returned to delete authorized resource'):
            assert response.status_code == 204
            assert response.reason == "No Content"
            response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=headers)
            assert response.status_code == 404
            assert response.reason == "Not Found"

        resource_path = f'authorize/{self.resource_id}'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=resource_path, headers=self.headers)
        with allure.step(
                'Proper status_code, reason and response data should be returned created authorized resource'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            assert json_response['resourceId'] == self.resource_id
            assert json_response['userId'] == user_guid
            assert json_response['creationDate'].startswith(get_formatted_date_str(_date_format='%Y-%m-%d'))