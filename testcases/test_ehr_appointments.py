
from urllib import response
import requests
import json
import pytest

from pages.appointment_api_page import AppointmentsApiPage
from testcases.base_test import BaseTest
from utils.helper import get_formatted_date_str
from utils.request_handler import RequestHandler
import jwt
import allure
import datetime
import re
from utils.dbConfig import DB
from resources.data import Data
from jsonschema.validators import  validate

start_date = get_formatted_date_str(_days=-3, _date_format='%Y-%m-%d')
end_date = get_formatted_date_str(_date_format='%Y-%m-%d')
class TestEHRAppointments(BaseTest):
    def setup_class(self):
        self.appointment = AppointmentsApiPage()
    # @pytest.fixture(autouse=True)
    # def setup_testcase(self):
    #     yield

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_appointments_loaded_properly_for_a_specific_date_range_with_valid_provider(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&endDate={end_date}&startDate={start_date}&doctorId={doctor_id}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper datalist, status_code and reason should be returned for all appointments'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            assert json_response['message'] == 'success'
            assert json_response['code'] == '000'
            data_list = json_response['dataList']
            for data in data_list:
                assert len(data['uuid']) == 36
                assert len(data['appointmentId']) == 7
                assert re.fullmatch(r'\d+', data['patientId'])
                assert len(data['patientFirstName']) > 0
                assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['patientBirthDate'])
                assert re.fullmatch(r'[mfoMFO]', data['patientGender'])
                assert re.fullmatch(r'\d{2}:\d{2} [AP]M', data['appointmentStartTime'])

        with open('resources/json_data/ehr_appointments_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_appointments_loaded_properly_for_a_specific_date_with_valid_provider(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&startDate={end_date}&doctorId={doctor_id}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper datalist, status_code and reason should be returned for all appointments'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            assert json_response['message'] == 'success'
            assert json_response['code'] == '000'
            data_list = json_response['dataList']
            for data in data_list:
                assert len(data['uuid']) == 36
                assert len(data['appointmentId']) == 7
                assert re.fullmatch(r'\d+', data['patientId'])
                assert len(data['patientFirstName']) > 0
                assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['patientBirthDate'])
                assert re.fullmatch(r'[mfoMFO]', data['patientGender'])
                assert re.fullmatch(r'\d{2}:\d{2} [AP]M', data['appointmentStartTime'])

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_appointments_should_not_load_without_provider_id_returns_proper_msg(self):
        request_path = f'lynx/appointments?cache.invalidateCache=true&endDate={end_date}&startDate={start_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper datalist, status_code and reason should be returned for all appointments'):
            assert response.status_code == 500
            assert response.reason == 'Internal Server Error'
            json_response = response.json()
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert json_response['path'] == '/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_without_start_date_as_params(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 500
            assert response.reason == 'Internal Server Error'
            json_response = response.json()
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert json_response['path'] == '/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_without_doctor_id_and_start_date_as_params(self):
        request_path = f'lynx/appointments?cache.invalidateCache=true&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 500
            assert response.reason == 'Internal Server Error'
            json_response = response.json()
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert json_response['path'] == '/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_data_using_start_date_after_end_date_as_params(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={end_date}&endDate={start_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 400
            assert response.reason == 'Bad Request'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 400
            assert json_response['error'] == 'Bad Requestr'
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_data_for_valid_doctor_id_with_token_from_another_ehr_lynx_enabled_user(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider1'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Unauthorized access. Provider Level.'
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_appointment_data_with_token_from_another_ehr_and_lynx_disabled_user(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 500
            assert response.reason == 'Internal Server Error'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            # assert 'No GUID found in the request' in json_response['message']
            assert 'query did not return a unique result' in json_response['message']
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_appointment_data_with_ehr_and_lynx_disabled_id_token(self):
        doctor_id = pytest.configs.get_config('rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 500
            assert response.reason == 'Internal Server Error'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            # assert 'No GUID found in the request' in json_response['message']
            assert 'query did not return a unique result' in json_response['message']
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_data_with_token_from_another_ehr_disabled_lynx_enabled_user(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Unauthorized access. Provider Level.'
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_data_with_ehr_disabled_lynx_enabled_id_and_token(self):
        doctor_id = pytest.configs.get_config('lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 500
            assert response.reason == 'Internal Server Error'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert json_response['message'] == f'The DoctorId {doctor_id} is not integrated with any Provider.'
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_appointment_data_with_expired_token(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(request_path=request_path,
                                                   token=pytest.configs.get_config('ehr_lynx_enabled_rt_provider_expired_token'))
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    # 2 test case has same name on 450 line
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_patient_meta_data_with_algorithm_set_as_none_token(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(request_path=request_path,
                                                   token=pytest.configs.get_config('token_with_algorithm_set_as_none'))
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_appointment_data_with_invalid_token(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(request_path=request_path,
                                                   token=pytest.configs.get_config('ehr_lynx_enabled_rt_provider_invalid_token'))
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_appointment_data_with_recently_blocked_provider_token(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_rt_provider')
        token = RequestHandler.get_auth_token(user_name=self.user_name,
                                              password=pytest.configs.get_config('all_provider_password'))
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        #Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(request_path=request_path, token=token)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_appointment_data_with_fake_token_created_with_valid_provider(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(request_path=request_path,
                                                   token=pytest.configs.get_config('rt_provider_fake_token_with_valid_provider'))
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_appointment_data_with_fake_token_created_with_expiration_date_updated(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(request_path=request_path,
                                                   token=pytest.configs.get_config('lynx_enabled_rt_provider_fake_expired_date_token'))
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_data_for_invalid_date_format(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        invalid_formatted_end_date = get_formatted_date_str(_date_format='%d-%m-%y')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={invalid_formatted_end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 500
            assert response.reason == 'Internal Server Error'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 500
            assert json_response['error'] == 'Internal Server Error'
            assert json_response['message'] == f"Text '{invalid_formatted_end_date}' could not be parsed at index 0"
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_appointment_data_for_ehr_linx_disabled_doctor_id(self):
        doctor_id = pytest.configs.get_config('rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Unauthorized access. Provider Level.'
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_data_for_ehr_disabled_lynx_enabled_doctor_id(self):
        doctor_id = pytest.configs.get_config('lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Unauthorized access. Provider Level.'
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_data_with_invalid_doctor_id(self):
        doctor_id = pytest.configs.get_config('invalid_doctor_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Unauthorized access. Provider Level.'
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.regression
    def test_doctor_should_not_get_ehr_appointment_data_for_blocked_doctor_id(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_rt_provider')
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')

        blocked_doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={blocked_doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider1'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['timestamp']
            assert json_response['status'] == 401
            assert json_response['error'] == 'Unauthorized'
            assert json_response['message'] == 'Unauthorized access. Provider Level.'
            assert json_response['path'] == f'/lynx/appointments'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sanity
    def test_get_ehr_ping_return_proper_msg(self):
        request_path = f'ping'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            assert response.text == 'Server is running'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sanity
    def test_get_ehr_cache_ping_return_proper_msg(self):
        request_path = f'cache/ping'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            assert response.text == 'PONG'

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_ehr_patient_meta_data_with_invalidateCache_true(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&startDate={start_date}&endDate={end_date}&doctorId={doctor_id}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)

        json_response = response.json()
        uuid = json_response['dataList'][0]['uuid']
        noteid = json_response['dataList'][0]['appointmentId']
        request_path = f'lynx/patient-metadata/{uuid}?noteId={noteid}&cache.invalidateCache=true'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            assert json_response['message'] == 'success'
            assert json_response['code'] == '000'
            assert json_response['data']['noteId'] == noteid
            assert json_response['data']['ehrAppointmentUuid'] == uuid

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_security_doctor_should_not_get_ehr_patient_meta_data_with_algorithm_set_as_none_token(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&startDate={start_date}&doctorId={doctor_id}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)

        json_response = response.json()
        uuid = json_response['dataList'][0]['uuid']
        noteid = json_response['dataList'][0]['appointmentId']
        request_path = f'lynx/patient-metadata/{uuid}?noteId={noteid}&cache.invalidateCache=true'
        response = RequestHandler.get_api_response(request_path=request_path, token=pytest.configs.get_config('token_with_algorithm_set_as_none'))
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_appointments_loaded_properly_for_a_specific_date_range_with_valid_provider_endpoint(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&endDate={end_date}&startDate={start_date}&doctorId={doctor_id}'
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
    def test_put_method_should_not_support_for_appointments_loaded_properly_for_a_specific_date_range_with_valid_provider_endpoint(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&endDate={end_date}&startDate={start_date}&doctorId={doctor_id}'
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
    def test_patch_method_should_not_support_for_appointments_loaded_properly_for_a_specific_date_range_with_valid_provider_endpoint(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&endDate={end_date}&startDate={start_date}&doctorId={doctor_id}'
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
    def test_delete_method_should_not_support_for_appointments_loaded_properly_for_a_specific_date_range_with_valid_provider_endpoint(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&endDate={end_date}&startDate={start_date}&doctorId={doctor_id}'
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
    def test_post_method_should_not_support_for_get_ehr_patient_meta_data_with_cache_true_endpoint(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&startDate={start_date}&doctorId={doctor_id}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)

        json_response = response.json()
        uuid = json_response['dataList'][0]['uuid']
        noteid = json_response['dataList'][0]['appointmentId']
        request_path = f'lynx/patient-metadata/{uuid}?noteId={noteid}&cache.invalidateCache=true'
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
    def test_put_method_should_not_support_for_get_ehr_patient_meta_data_with_cache_true_endpoint(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&startDate={start_date}&doctorId={doctor_id}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)

        json_response = response.json()
        uuid = json_response['dataList'][0]['uuid']
        noteid = json_response['dataList'][0]['appointmentId']
        request_path = f'lynx/patient-metadata/{uuid}?noteId={noteid}&cache.invalidateCache=true'
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
    def test_patch_method_should_not_support_for_get_ehr_patient_meta_data_with_cache_true_endpoint(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&startDate={start_date}&doctorId={doctor_id}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)

        json_response = response.json()
        uuid = json_response['dataList'][0]['uuid']
        noteid = json_response['dataList'][0]['appointmentId']
        request_path = f'lynx/patient-metadata/{uuid}?noteId={noteid}&cache.invalidateCache=true'
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
    def test_delete_method_should_not_support_for_get_ehr_patient_meta_data_with_cache_true_endpoint(self):
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
        request_path = f'lynx/appointments?cache.invalidateCache=true&startDate={start_date}&doctorId={doctor_id}'
        response = RequestHandler.get_api_response(user_name=pytest.configs.get_config('ehr_lynx_enabled_rt_provider'),
                                                   password=pytest.configs.get_config('all_provider_password'),
                                                   request_path=request_path)

        json_response = response.json()
        uuid = json_response['dataList'][0]['uuid']
        noteid = json_response['dataList'][0]['appointmentId']
        request_path = f'lynx/patient-metadata/{uuid}?noteId={noteid}&cache.invalidateCache=true'
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
    def test_post_method_should_not_support_for_get_ehr_ping_endpoint(self):
        request_path = f'ping'
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
    def test_put_method_should_not_support_for_get_ehr_ping_endpoint(self):
        request_path = f'ping'
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
    def test_patch_method_should_not_support_for_get_ehr_ping_endpoint(self):
        request_path = f'ping'
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
    def test_delete_method_should_not_support_for_get_ehr_ping_endpoint(self):
        request_path = f'ping'
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
    def test_post_method_should_not_support_for_get_ehr_cache_ping_endpoint(self):
        request_path = f'cache/ping'
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
    def test_put_method_should_not_support_for_get_ehr_cache_ping_endpoint(self):
        request_path = f'cache/ping'
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
    def test_patch_method_should_not_support_for_get_ehr_cache_ping_endpoint(self):
        request_path = f'cache/ping'
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
    def test_delete_method_should_not_support_for_get_ehr_cache_ping_endpoint(self):
        request_path = f'cache/ping'
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
            
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.usefixtures("setup_for_password_reset_testcases")
    @pytest.mark.security
    def test_doctor_should_not_get_ehr_appointment_data_with_changed_password_previous_token(self):
        self.user_name = pytest.configs.get_config('ehr_lynx_enabled_rt_provider2')
        token = RequestHandler.get_auth_token(user_name=self.user_name,
                                              password=pytest.configs.get_config('all_provider_password'))
        doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider2_id')

        self.password_hash = pytest.configs.get_config("ehr_lynx_enabled_rt_provider2_password_hash")
        self.appointment.reset_password(token=token, new_password='@ugmed1X@1')

        request_path = f'lynx/appointments?cache.invalidateCache=true&doctorId={doctor_id}&startDate={start_date}&endDate={end_date}'
        response = RequestHandler.get_api_response(request_path=request_path, token=token)
        with allure.step('Proper massage, status_code and reason should be returned'):
            assert response.status_code == 401
            assert response.reason == "Unauthorized"