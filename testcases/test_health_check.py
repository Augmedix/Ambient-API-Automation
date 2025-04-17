
from urllib import response
import requests
import json
import pytest
from utils.helper import get_formatted_date_str
from utils.request_handler import RequestHandler
from utils.api_request_data_handler import APIRequestDataHandler
import jwt
import allure
import datetime
import re
from utils.dbConfig import DB
from resources.data import Data
import jsonschema
from jsonschema.validators import  validate, Draft7Validator, create






class TestHealthCheck:
    appointments_base_url = pytest.configs.get_config('appointments_base_url')
    authorization_base_url = pytest.configs.get_config('authorization_base_url')



    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.health_check
    def test_get_ehr_health_check_return_proper_msg(self):
        request_path = f'health-check'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)

        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            # assert json_response['ATHENA-TEST'] == True
            assert json_response['cache'] == True
            assert json_response['phiDb'] == True
            # assert json_response['CHI_A'] == True
            assert json_response['axDb'] == True

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.health_check
    def test_appointments_service_api_health(self):
        health_path = 'open/health'
        api_response = RequestHandler.get_api_response(base_url=self.appointments_base_url, request_path=health_path,
                                                       user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                       password=pytest.configs.get_config("all_provider_password"))

        request_body = APIRequestDataHandler('appointments_data')
        expected_response = json.loads(json.dumps(request_body.get_payload("health")))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert api_response.status_code == 200
            assert api_response.reason == 'OK'
            json_response = api_response.json()
            assert json_response['status'] == expected_response['status']
            assert json_response['applicationName'] == expected_response['applicationName']
            assert json_response['serverPort'] == expected_response['serverPort']
            assert json_response['platformVersion']
            assert json_response['publicReleaseVersion']
            assert json_response['details']['memory']['total']
            assert json_response['details']['memory']['max'] <= expected_response['details']['memory']['max']
        with open('resources/json_data/appointments_health_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.health_check
    def test_get_auth_health(self):
        path_auth__health = 'auth/v1/open/health'
        response = RequestHandler.get_api_response(base_url=pytest.configs.get_config('base_url'), request_path=path_auth__health)
        json_response = response.json
        with open('resources/json_data/auth_health.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            assert expected_response['status'] == json_response['status']
            assert expected_response['applicationName'] == json_response['applicationName']
            assert expected_response['serverPort'] == json_response['serverPort']
            assert expected_response['platformVersion']
            assert expected_response['details']['db']['augmedix'] == json_response['details']['db']['augmedix']
            assert expected_response['details']['db']['wfm'] == json_response['details']['db']['wfm']
        
        with open('resources/json_data/auth_health_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.health_check
    def test_authorization_service_api_health(self):
        health_path = 'open/health'
        api_response = RequestHandler.get_api_response(base_url=self.authorization_base_url, request_path=health_path,
                                                       user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                       password=pytest.configs.get_config("all_provider_password"))

        request_body = APIRequestDataHandler('authorization')
        authorize_service_health_expected_schema = json.loads(json.dumps(request_body.get_modified_payload(name="authorize_service_health_schema")))
        expected_response = json.loads(json.dumps(request_body.get_payload("health")))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert api_response.status_code == 200
            assert api_response.reason == 'OK'
            json_response = api_response.json()
            assert json_response['status'] == expected_response['status']
            assert json_response['applicationName'] == expected_response['applicationName']
            assert json_response['serverPort'] == expected_response['serverPort']
            assert json_response['platformVersion']
            assert json_response['publicReleaseVersion']
            assert json_response['details']['memory']['total']
            assert json_response['details']['memory']['max']
        with allure.step('json schema is validated'):
            assert validate(json_response, authorize_service_health_expected_schema) is None


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_ehr_health_check_endpoint(self):
        request_path = f'health-check'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_type='POST',
                                                   request_path=request_path)

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_ehr_health_check_endpoint(self):
        request_path = f'health-check'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_type='PUT',
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
    def test_patch_method_should_not_support_for_get_ehr_health_check_endpoint(self):
        request_path = f'health-check'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_type='PATCH',
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
    def test_delete_method_should_not_support_for_get_ehr_health_check_endpoint(self):
        request_path = f'health-check'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_type='DELETE',
                                                   request_path=request_path)

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_appointments_service_api_health_endpoint(self):
        health_path = 'open/health'
        response = RequestHandler.get_api_response(base_url=self.appointments_base_url, request_path=health_path,
                                                       request_type='POST',
                                                       user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                       password=pytest.configs.get_config("all_provider_password"))

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_appointments_service_api_health_endpoint(self):
        health_path = 'open/health'
        response = RequestHandler.get_api_response(base_url=self.appointments_base_url, request_path=health_path,
                                                       request_type='PUT',
                                                       user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                       password=pytest.configs.get_config("all_provider_password"))

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_appointments_service_api_health_endpoint(self):
        health_path = 'open/health'
        response = RequestHandler.get_api_response(base_url=self.appointments_base_url, request_path=health_path,
                                                       request_type='PATCH',
                                                       user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                       password=pytest.configs.get_config("all_provider_password"))

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_appointments_service_api_health_endpoint(self):
        health_path = 'open/health'
        response = RequestHandler.get_api_response(base_url=self.appointments_base_url, request_path=health_path,
                                                       request_type='DELETE',
                                                       user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                       password=pytest.configs.get_config("all_provider_password"))

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_auth_health_endpoint(self):
        path_auth__health = 'auth/v1/open/health'
        response = RequestHandler.get_api_response(base_url=pytest.configs.get_config('base_url'), 
                                                   request_type='POST',
                                                   request_path=path_auth__health)

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_auth_health_endpoint(self):
        path_auth__health = 'auth/v1/open/health'
        response = RequestHandler.get_api_response(base_url=pytest.configs.get_config('base_url'), 
                                                   request_type='PUT',
                                                   request_path=path_auth__health)

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_auth_health_endpoint(self):
        path_auth__health = 'auth/v1/open/health'
        response = RequestHandler.get_api_response(base_url=pytest.configs.get_config('base_url'), 
                                                   request_type='PATCH',
                                                   request_path=path_auth__health)

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_get_auth_health_endpoint(self):
        path_auth__health = 'auth/v1/open/health'
        response = RequestHandler.get_api_response(base_url=pytest.configs.get_config('base_url'), 
                                                   request_type='DELETE',
                                                   request_path=path_auth__health)

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_authorization_service_api_health_endpoint(self):
        health_path = 'open/health'
        response = RequestHandler.get_api_response(base_url=self.authorization_base_url, request_path=health_path,
                                                   request_type='POST',
                                                   user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"))

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_authorization_service_api_health_endpoint(self):
        health_path = 'open/health'
        response = RequestHandler.get_api_response(base_url=self.authorization_base_url, request_path=health_path,
                                                   request_type='PUT',
                                                   user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"))

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_authorization_service_api_health_endpoint(self):
        health_path = 'open/health'
        response = RequestHandler.get_api_response(base_url=self.authorization_base_url, request_path=health_path,
                                                   request_type='PATCH',
                                                   user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"))

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_authorization_service_api_health_endpoint(self):
        health_path = 'open/health'
        response = RequestHandler.get_api_response(base_url=self.authorization_base_url, request_path=health_path,
                                                   request_type='DELETE',
                                                   user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"))

        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"
            
            
