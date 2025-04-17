import json

import allure
import pytest
from jsonschema.validators import validate

from pages.complaints_api_page import ComplaintsApiPage
from resources.data import Data
from testcases.base_test import BaseTest
from utils.db_manager import DBManager
from utils.request_handler import RequestHandler

respond = None


class TestComplaints(BaseTest):
    base_url = pytest.configs.get_config('note_builder_base_url')
    lynx_hpi_chronic_blocks = Data.lynx_hpi_chronic_blocks
    lynx_ap_chronic_blocks = Data.lynx_ap_chronic_blocks
    lynx_hpi_acute_blocks = Data.lynx_hpi_acute_blocks
    lynx_ap_acute_blocks = Data.lynx_ap_acute_blocks

    @pytest.fixture(scope='class', autouse=True)
    def setup_suite(self, request):
        self.db_manager = DBManager(db_name='augmedixnotebuilder')
        self.db_manager.start_tunnel()

        request.cls.complaints = ComplaintsApiPage(self.db_manager)
        request.cls.chronic_complaint_id, self.chronic_complaint_name = self.complaints.get_first_complaints("CHRONIC")
        request.cls.acute_complaint_id, self.acute_complaint_name = self.complaints.get_first_complaints("ACUTE")
        request.cls.visit_complaint_id, self.visit_complaint_name = self.complaints.get_first_complaints("VISIT")

        yield

        self.db_manager.stop_tunnel()

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_if_isMobile_flag_true(self):
        expected_variation_id_list = self.complaints.get_complaint_element_variations_id_based_on_mobile_flag(complaints_id=self.acute_complaint_id, mobile_flag=1)
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=true'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path)

        actual_variation_id =[]
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            hpiBlocks = json_response["hpiBlocks"]
            apBlocks = json_response["apBlocks"]
            for i in range(len(hpiBlocks)):
                assert hpiBlocks[i]['section'] == 'HPI'
                assert hpiBlocks[i]['isPublished']
                assert hpiBlocks[i]['name'] in self.lynx_hpi_acute_blocks
                actual_variation_id.append(hpiBlocks[i]['elementVariationId'])
            for i in range(len(apBlocks)):
                assert apBlocks[i]['section'] == 'AP'
                assert apBlocks[i]['isPublished'] == True
                assert apBlocks[i]['name'] in self.lynx_ap_acute_blocks
                actual_variation_id.append(apBlocks[i]['elementVariationId'])
            actual_variation_id.sort()
            expected_variation_id_list.sort()
            print(f'Actual: {actual_variation_id}\nExpected: {expected_variation_id_list}')
            assert actual_variation_id == expected_variation_id_list
        with open('resources/json_data/acute_complaints_data_isMobile_true_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None    

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_all_variation_blocks_for_specific_notebuilder_chronic_complaints_if_isMobile_flag_true(self):
        expected_variation_id_list = self.complaints.get_complaint_element_variations_id_based_on_mobile_flag(complaints_id=self.chronic_complaint_id, mobile_flag=1)
        request_path = f'complaints/{self.chronic_complaint_id}?isMobile=true'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path)
        actual_variation_id =[]
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            hpiBlocks = json_response["hpiBlocks"]
            apBlocks = json_response["apBlocks"]
            for i in range(len(hpiBlocks)):
                assert hpiBlocks[i]['section'] == 'HPI'
                assert hpiBlocks[i]['isPublished'] == True
                assert hpiBlocks[i]['name'] in self.lynx_hpi_chronic_blocks
                actual_variation_id.append(hpiBlocks[i]['elementVariationId'])
            for i in range(len(apBlocks)):
                assert apBlocks[i]['section'] == 'AP'
                assert apBlocks[i]['isPublished'] == True
                assert apBlocks[i]['name'] in self.lynx_ap_chronic_blocks
                actual_variation_id.append(apBlocks[i]['elementVariationId'])
            actual_variation_id.sort()
            expected_variation_id_list.sort()
            print(f'Actual: {actual_variation_id}\nExpected: {expected_variation_id_list}')
            assert actual_variation_id == expected_variation_id_list
        with open('resources/json_data/chronic_complaints_data_isMobile_true_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None    

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_all_variation_blocks_for_specific_notebuilder_visit_complaints_if_isMobile_flag_true(self):
        expected_variation_id_list = self.complaints.get_complaint_element_variations_id_based_on_mobile_flag(
            complaints_id=self.visit_complaint_id, mobile_flag=1)
        request_path = f'complaints/{self.visit_complaint_id}?isMobile=true'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path)
        actual_variation_id = []
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            hpiBlocks = json_response["hpiBlocks"]
            apBlocks = json_response["apBlocks"]
            for i in range(len(hpiBlocks)):
                assert hpiBlocks[i]['section'] == 'HPI'
                assert hpiBlocks[i]['isPublished'] == True
                assert hpiBlocks[i]['name']
                actual_variation_id.append(hpiBlocks[i]['elementVariationId'])
            for i in range(len(apBlocks)):
                assert apBlocks[i]['section'] == 'AP'
                assert apBlocks[i]['isPublished'] == True
                assert apBlocks[i]['name']
                actual_variation_id.append(apBlocks[i]['elementVariationId'])
            actual_variation_id.sort()
            expected_variation_id_list.sort()
            print(f'Actual: {actual_variation_id}\nExpected: {expected_variation_id_list}')
            assert actual_variation_id == expected_variation_id_list
        with open('resources/json_data/visit_complaints_data_isMobile_true_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None    


    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_expired_token_if_isMobile_flag_is_true(self):
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=true'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_expired_token'))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"


    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_chronic_complaints_with_invalid_token_if_isMobile_flag_is_true(self):
        request_path = f'complaints/{self.chronic_complaint_id}?isMobile=true'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_invalid_token'))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_recently_blocked_provider_token_if_isMobile_flag_is_true(self):
        self.user_name = pytest.configs.get_config('lynx_enabled_rt_provider')
        token = RequestHandler.get_auth_token(user_name=self.user_name,
                                              password=pytest.configs.get_config('all_provider_password'))
        #Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=true'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path, token=token)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.security
    # def test_should_not_get_notebuilder_complaints_with_lynx_disabled_provider_token_for_specific_id_if_isMobile_flag_is_true(self):
    #     token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config('lynx_disabled_rt_provider_email'),
    #                                                     password=pytest.configs.get_config('lynx_disabled_rt_provider_password'))
    #     request_path = f'complaints/62?isMobile=true'
    #     response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path, token=token)
    #     with allure.step('Proper dataset, status_code and reason should be returned'):
    #         assert response.status_code == 401
    #         assert response.reason == "Unauthorized"

    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.security
    # def test_should_not_get_notebuilder_complaints_with_different_provider_token_for_specific_id_if_isMobile_flag_is_true(self):
    #     token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
    #                                           password=pytest.configs.get_config("all_provider_password"))
    #     request_path = f'complaints/62?isMobile=true'
    #     response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path, token=token)
    #     with allure.step('Proper dataset, status_code and reason should be returned'):
    #         assert response.status_code == 401
    #         assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_fake_token_created_with_valid_provider_if_isMobile_flag_is_true(self):
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=true'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_token_with_valid_provider'))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_fake_token_created_with_expiration_date_updated_if_isMobile_flag_is_true(self):
        request_path = f'complaints/62?isMobile=true'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_expired_date_token'))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_if_isMobile_flag_false(self):
        expected_variation_id_list = self.complaints.get_complaint_element_variations_id_based_on_mobile_flag(
            complaints_id=self.acute_complaint_id, mobile_flag=0)
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=false'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path)
        actual_variation_id = []
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            hpiBlocks = json_response["hpiBlocks"]
            apBlocks = json_response["apBlocks"]
            for i in range(len(hpiBlocks)):
                assert hpiBlocks[i]['section'] == 'HPI'
                assert hpiBlocks[i]['isPublished'] == True
                assert hpiBlocks[i]['name']
                actual_variation_id.append(hpiBlocks[i]['elementVariationId'])
            for i in range(len(apBlocks)):
                assert apBlocks[i]['section'] == 'AP'
                assert apBlocks[i]['isPublished'] == True
                assert apBlocks[i]['name']
                actual_variation_id.append(apBlocks[i]['elementVariationId'])
            actual_variation_id.sort()
            expected_variation_id_list.sort()
            print(f'Actual: {actual_variation_id}\nExpected: {expected_variation_id_list}')
            assert actual_variation_id == expected_variation_id_list
        with open('resources/json_data/acute_complaints_data_isMobile_false_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None    

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_all_variation_blocks_for_specific_notebuilder_chronic_complaints_if_isMobile_flag_false(self):
        expected_variation_id_list = self.complaints.get_complaint_element_variations_id_based_on_mobile_flag(
            complaints_id=self.chronic_complaint_id, mobile_flag=0)
        request_path = f'complaints/{self.chronic_complaint_id}?isMobile=false'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path)
        actual_variation_id = []
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            hpiBlocks = json_response["hpiBlocks"]
            apBlocks = json_response["apBlocks"]
            for i in range(len(hpiBlocks)):
                assert hpiBlocks[i]['section'] == 'HPI'
                assert hpiBlocks[i]['isPublished'] == True
                assert hpiBlocks[i]['name']
                actual_variation_id.append(hpiBlocks[i]['elementVariationId'])
            for i in range(len(apBlocks)):
                assert apBlocks[i]['section'] == 'AP'
                assert apBlocks[i]['isPublished'] == True
                assert apBlocks[i]['name']
                actual_variation_id.append(apBlocks[i]['elementVariationId'])
            actual_variation_id.sort()
            expected_variation_id_list.sort()
            print(f'Actual: {actual_variation_id}\nExpected: {expected_variation_id_list}')
            assert actual_variation_id == expected_variation_id_list
        with open('resources/json_data/chronic_complaints_data_isMobile_false_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None   


    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_all_variation_blocks_for_specific_notebuilder_visit_complaints_if_isMobile_flag_false(self):
        expected_variation_id_list = self.complaints.get_complaint_element_variations_id_based_on_mobile_flag(
            complaints_id=self.visit_complaint_id, mobile_flag=0)
        request_path = f'complaints/{self.visit_complaint_id}?isMobile=false'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path)
        actual_variation_id = []
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            hpiBlocks = json_response["hpiBlocks"]
            apBlocks = json_response["apBlocks"]
            for i in range(len(hpiBlocks)):
                assert hpiBlocks[i]['section'] == 'HPI'
                assert hpiBlocks[i]['isPublished'] == True
                assert hpiBlocks[i]['name']
                actual_variation_id.append(hpiBlocks[i]['elementVariationId'])
            for i in range(len(apBlocks)):
                assert apBlocks[i]['section'] == 'AP'
                assert apBlocks[i]['isPublished'] == True
                assert apBlocks[i]['name']
                actual_variation_id.append(apBlocks[i]['elementVariationId'])
            actual_variation_id.sort()
            expected_variation_id_list.sort()
            print(f'Actual: {actual_variation_id}\nExpected: {expected_variation_id_list}')
            assert actual_variation_id == expected_variation_id_list
        with open('resources/json_data/visit_complaints_data_isMobile_false_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None   



    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_expired_token_if_isMobile_flag_is_false(self):
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=false'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_expired_token'))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_invalid_token_if_isMobile_flag_is_false(self):
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=false'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_invalid_token'))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_recently_blocked_provider_token_if_isMobile_flag_is_false(self):
        self.user_name = pytest.configs.get_config('lynx_enabled_rt_provider')
        token = RequestHandler.get_auth_token(user_name=self.user_name,
                                              password=pytest.configs.get_config('all_provider_password'))
        #Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=false'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path, token=token)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.security
    # def test_should_not_get_notebuilder_complaints_with_lynx_disabled_provider_token_for_specific_id_if_isMobile_flag_is_false(self):
    #     token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config('lynx_disabled_rt_provider_email'),
    #                                                     password=pytest.configs.get_config('lynx_disabled_rt_provider_password'))
    #     request_path = f'complaints/62?isMobile=false'
    #     response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path, token=token)
    #     with allure.step('Proper dataset, status_code and reason should be returned'):
    #         assert response.status_code == 401
    #         assert response.reason == "Unauthorized"

    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.security
    # def test_should_not_get_notebuilder_complaints_with_different_provider_token_for_specific_id_if_isMobile_flag_is_false(self):
    #     token = RequestHandler.get_auth_token(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
    #                                           password=pytest.configs.get_config("all_provider_password"))
    #     request_path = f'complaints/62?isMobile=false'
    #     response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path, token=token)
    #     with allure.step('Proper dataset, status_code and reason should be returned'):
    #         assert response.status_code == 401
    #         assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_fake_token_created_with_valid_provider_if_isMobile_flag_is_false(self):
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=false'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_token_with_valid_provider'))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_should_not_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_fake_token_created_with_expiration_date_updated_if_isMobile_flag_is_false(self):
        request_path = f'complaints/{self.acute_complaint_id}?isMobile=false'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_expired_date_token'))
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_all_notebuilder_complaints(self):
        request_path = f'complaints'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path)
        json_response = response.json()
        with open('resources/json_data/notebuilder_complaints_all_data.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            # assert expected_response == json_response

    
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_should_not_get_all_notebuilder_complaints_algorithm_set_as_none_token(self):
        request_path = f'complaints'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path,
                                                   token=pytest.configs.get_config('token_with_algorithm_set_as_none'))
        with allure.step('Proper status_code and reason should be returned for expired user token'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_all_notebuilder_complaints_endpoint(self):
        request_path = f'complaints'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path, request_type='POST')
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 403
            assert response.reason == 'Forbidden'
            json_response = response.json()
            assert json_response['statusCode'] == 403
            assert json_response['error'] == 'Forbidden'
            assert json_response['message'] == "Permission denied."


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_all_notebuilder_complaints_endpoint(self):
        request_path = f'complaints'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path, request_type='PUT')
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 404
            assert response.reason == 'Not Found'
            json_response = response.json()
            assert json_response['statusCode'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == "Cannot PUT /complaints"


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_all_notebuilder_complaints_endpoint(self):
        request_path = f'complaints'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path, request_type='PATCH')
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 404
            assert response.reason == 'Not Found'
            json_response = response.json()
            assert json_response['statusCode'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == "Cannot PATCH /complaints"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_get_all_notebuilder_complaints_endpoint(self):
        request_path = f'complaints'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path, request_type='DELETE')
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 404
            assert response.reason == 'Not Found'
            json_response = response.json()
            assert json_response['statusCode'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == "Cannot DELETE /complaints"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_changed_password_previous_token_if_isMobile_flag_is_true(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_rt_provider2')
        token = RequestHandler.get_auth_token(user_name=self.user_name,
                                              password=pytest.configs.get_config('all_provider_password'))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.complaints.reset_password(token=token, new_password='@ugmed1X@11')

        request_path = f'complaints/{self.acute_complaint_id}?isMobile=true'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path, token=token)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_should_not_get_all_variation_blocks_for_specific_notebuilder_acute_complaints_with_changed_password_previous_token_if_isMobile_flag_is_false(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_rt_provider2')
        token = RequestHandler.get_auth_token(user_name=self.user_name,
                                              password=pytest.configs.get_config('all_provider_password'))
        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.complaints.reset_password(token=token, new_password='@ugmed1X@1')

        request_path = f'complaints/{self.acute_complaint_id}?isMobile=false'
        response = RequestHandler.get_api_response(base_url=self.base_url, request_path=request_path, token=token)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_error_message_when_the_complaints_id_invalid(self):
        request_path = f'complaints/a123?isMobile=true'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path)
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 404
            assert response.reason == "Not Found"
            json_response = response.json()
            assert json_response['statusCode'] == 404
            assert json_response['error'] == 'Not Found'
            assert json_response['message'] == "Could not find any entity of type \"ComplaintEntity\" matching: null"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_get_all_variation_blocks_for_specific_notebuilder_visit_complaints_without_mobile_flag_as_query_params(self):
        expected_variation_id_list = self.complaints.get_complaint_element_variations_id_based_on_mobile_flag(
            complaints_id=self.visit_complaint_id, mobile_flag=0)
        request_path = f'complaints/{self.visit_complaint_id}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config("lynx_enabled_rt_provider"),
                                                   password=pytest.configs.get_config("all_provider_password"),
                                                   base_url=self.base_url, request_path=request_path)
        actual_variation_id = []
        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            hpiBlocks = json_response["hpiBlocks"]
            apBlocks = json_response["apBlocks"]
            for i in range(len(hpiBlocks)):
                assert hpiBlocks[i]['section'] == 'HPI'
                assert hpiBlocks[i]['isPublished'] == True
                assert hpiBlocks[i]['name']
                actual_variation_id.append(hpiBlocks[i]['elementVariationId'])
            for i in range(len(apBlocks)):
                assert apBlocks[i]['section'] == 'AP'
                assert apBlocks[i]['isPublished'] == True
                assert apBlocks[i]['name']
                actual_variation_id.append(apBlocks[i]['elementVariationId'])
            actual_variation_id.sort()
            expected_variation_id_list.sort()
            print(f'Actual: {actual_variation_id}\nExpected: {expected_variation_id_list}')
            assert actual_variation_id == expected_variation_id_list
        with open('resources/json_data/visit_complaints_data_isMobile_false_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None
