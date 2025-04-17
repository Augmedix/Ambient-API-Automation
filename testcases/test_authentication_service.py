import json
import pytest

from pages.appointment_api_page import AppointmentsApiPage
from resources.data import Data
from testcases.base_test import BaseTest
from utils.request_handler import RequestHandler
from utils.dbConfig import DB
import jwt
import allure


class TestAuthenticationService(BaseTest):

    def setup_class(self):
        self.appointment = AppointmentsApiPage()
        self.db = DB()
        self.data = Data()

    @pytest.fixture
    def setup_testcase_for_specific_testcases_auth(self):
        yield
        RequestHandler.get_auth_response(user_name=self.user_name,
                                         password=pytest.configs.get_config("all_provider_password"))

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_login_with_valid_lynx_enabled_provider_credential_generates_token(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"),
                                                    printData=True)
        with allure.step('Proper token, status_code and reason should be returned for valid lynx enabled user'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            assert len(json_response['token']) == 235

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_validate_token_contains_guid_for_valid_lynx_enabled_provider(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"),
                                                    printData=True)

        with allure.step('Proper guid should be returned for valid lynx enabled user'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
            assert json_response['token']
            assert decoded["iss"] == "com.augmedix"
            assert decoded["exp"]
            assert decoded["uid"] == int(pytest.configs.get_config("lynx_enabled_rt_provider_id"))
            assert decoded["rls"][0] == "DOCTOR"
            assert decoded["guid"] == pytest.configs.get_config("lynx_enabled_rt_provider_guid")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_validate_token_should_not_contains_guid_for_lynx_disabled_user_credential_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config('rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Token should not contains Guid'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
            assert json_response['token']
            assert decoded["iss"] == "com.augmedix"
            assert decoded["exp"]
            assert decoded["uid"] == int(pytest.configs.get_config("rt_provider_id"))
            assert decoded["rls"][0] == "DOCTOR"
            assert "guid" not in decoded

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_invalid_email_format_without_at_the_rate_sign_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name='test_lynx_api_lynx_enabled_rt_provider04augmedix.com',
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_invalid_email_format_without_part_after_dot_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name='test_lynx_api_lynx_enabled_rt_provider04@augmedix',
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_invalid_email_format_without_part_after_at_sign_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name='test_lynx_api_lynx_enabled_rt_provider04',
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_invalid_email_format_with_multiple_at_sign_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name='test_lynx_api_lynx_enabled_rt_provider04@@@@',
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_invalid_email_format_with_multiple_dot_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name='test_lynx_api_lynx_enabled_rt_provider04@augmedix.....com',
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_invalid_email_format_with_special_character_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name='test_lynx_api_lynx_enabled_rt_provider#@%^*&%()04@augmedix.....com',
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_blank_email_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name=' ',
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_specific_testcases_auth")
    @pytest.mark.regression
    def test_login_with_blank_password_return_proper_msg(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        response = RequestHandler.get_auth_response(user_name=self.user_name,
                                                    password=' ', printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid password'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_blank_email_and_password_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name=' ', password=' ', printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_unregistered_email_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name='unregistered@augmedix.com', printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_specific_testcases_auth")
    @pytest.mark.regression
    def test_login_with_invalid_password_return_proper_msg(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        response = RequestHandler.get_auth_response(user_name=self.user_name, password='invalidAx@13012', printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid password'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.regression
    def test_login_with_blocked_user_return_proper_msg(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        # Blocked user
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')

        response = RequestHandler.get_auth_response(user_name=self.user_name,
                                                    password=pytest.configs.get_config("all_provider_password"),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Account is currently blocked'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_valid_email_with_all_capital_letter_generates_token(self):
        user_name = 'TEST_LYNX_API_LYNX_ENABLED_RT_PROVIDER03@AUGMEDIX.COM'
        response = RequestHandler.get_auth_response(user_name=user_name.upper(),
                                                    password=pytest.configs.get_config("all_provider_password"),
                                                    printData=True)

        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
            assert json_response['token']
            assert decoded["iss"] == "com.augmedix"
            assert decoded["exp"]
            assert decoded["uid"] == int(pytest.configs.get_config("lynx_enabled_rt_provider_id"))
            assert decoded["rls"][0] == "DOCTOR"
            assert decoded["guid"] == pytest.configs.get_config("lynx_enabled_rt_provider_guid")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_valid_email_with_combination_of_lower_upper_case_letter_generates_token(self):
        response = RequestHandler.get_auth_response(user_name='TEST_lynx_API_lynx_enabled_rt_provider03@aUGMEDIX.CoM',
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
            assert json_response['token']
            assert decoded["iss"] == "com.augmedix"
            assert decoded["exp"]
            assert decoded["uid"] == int(pytest.configs.get_config("lynx_enabled_rt_provider_id"))
            assert decoded["rls"][0] == "DOCTOR"
            assert decoded["guid"] == pytest.configs.get_config("lynx_enabled_rt_provider_guid")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_specific_testcases_auth")
    @pytest.mark.regression
    def test_login_with_temporary_password_return_proper_msg(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_nrt_provider2')
        response = RequestHandler.get_auth_response(user_name=self.user_name,
                                                    password=pytest.configs.get_config('ehr_lynx_enabled_nrt_provider2_temporary_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid password'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.regression
    def test_try_to_login_with_invalid_password_four_times_to_block_the_user_return_proper_msg(self):
        self.user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
        for _ in range(4):
            response = RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23', printData=True)

        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Provider account blocked.'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_login_with_valid_lynx_enabled_rt_user_credential_generates_token(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper token, status_code and reason should be returned for valid nrt user'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
            assert json_response['token']
            assert decoded["iss"] == "com.augmedix"
            assert decoded["exp"]
            assert decoded["uid"] == int(pytest.configs.get_config("lynx_enabled_rt_provider_id"))
            assert decoded["rls"][0] == "DOCTOR"
            assert decoded["guid"] == pytest.configs.get_config("lynx_enabled_rt_provider_guid")

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_validate_guid_for_valid_rt_lynx_disabled_user_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config('rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Guid should not returned for valid lynx disable nrt user'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
            assert json_response['token']
            assert decoded["iss"] == "com.augmedix"
            assert decoded["exp"]
            assert decoded["uid"] == int(pytest.configs.get_config("rt_provider_id"))
            assert decoded["rls"][0] == "DOCTOR"
            assert "guid" not in decoded

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_validate_token_contains_guid_for_valid_rt_lynx_enabled_user_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)

        with allure.step('Guid should be generated properly'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
            assert json_response['token']
            assert decoded["iss"] == "com.augmedix"
            assert decoded["exp"]
            assert decoded["uid"] == int(pytest.configs.get_config("lynx_enabled_rt_provider_id"))
            assert decoded["rls"][0] == "DOCTOR"
            assert decoded["guid"] == pytest.configs.get_config('lynx_enabled_rt_provider_guid')

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_invalid_email_format_with_space_at_the_beginning_of_the_email_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name=" " + pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_valid_email_format_with_space_at_the_end_of_the_email_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config('lynx_enabled_rt_provider')+" ",
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)

        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == "OK"
            json_response = response.json()
            decoded = jwt.decode(json_response['token'], options={"verify_signature": False})
            assert json_response['token']
            assert decoded["iss"] == "com.augmedix"
            assert decoded["exp"]
            assert decoded["uid"] == int(pytest.configs.get_config("lynx_enabled_rt_provider_id"))
            assert decoded["rls"][0] == "DOCTOR"
            assert decoded["guid"] == pytest.configs.get_config("lynx_enabled_rt_provider_guid")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_login_with_invalid_email_format_with_semiclon_at_the_end_of_the_email_return_proper_msg(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config('lynx_enabled_rt_provider')+';',
                                                    password=pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid email'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_specific_testcases_auth")
    @pytest.mark.regression
    def test_login_with_valid_email_format_with_space_at_the_beginning_of_the_password_return_proper_msg(self):
        self.user_name = pytest.configs.get_config('lynx_enabled_rt_provider')
        response = RequestHandler.get_auth_response(user_name=self.user_name,
                                                    password=" " + pytest.configs.get_config('all_provider_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid password'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_specific_testcases_auth")
    @pytest.mark.regression
    def test_login_with_valid_email_format_with_space_at_the_end_of_the_password_return_proper_msg(self):
        self.user_name = pytest.configs.get_config('lynx_enabled_rt_provider')
        response = RequestHandler.get_auth_response(user_name=self.user_name,
                                                    password=pytest.configs.get_config('all_provider_password') + ' ',
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid password'
            assert json_response['path'] == '/token'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_specific_testcases_auth")
    @pytest.mark.regression
    def test_login_with_valid_email_format_with_previous_password_return_proper_msg(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_nrt_provider2')
        response = RequestHandler.get_auth_response(user_name=self.user_name,
                                                    password=pytest.configs.get_config('ehr_lynx_enabled_nrt_provider2_previous_password'),
                                                    printData=True)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Invalid password'
            assert json_response['path'] == '/token'

        
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_method_should_not_support_for_login_with_valid_lynx_enabled_provider_endpoint(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"),
                                                    request_type='GET',
                                                    printData=True)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'GET' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_login_with_valid_lynx_enabled_provider_endpoint(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"),
                                                    request_type='PUT',
                                                    printData=True)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_login_with_valid_lynx_enabled_provider_endpoint(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"),
                                                    request_type='PATCH',
                                                    printData=True)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_login_with_valid_lynx_enabled_provider_endpoint(self):
        response = RequestHandler.get_auth_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                    password=pytest.configs.get_config("all_provider_password"),
                                                    request_type='DELETE',
                                                    printData=True)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"


    