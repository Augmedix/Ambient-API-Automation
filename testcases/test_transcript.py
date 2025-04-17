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


class TestTranscript(BaseTest):
    transcript_base_url = pytest.configs.get_config('transcript_base_url')
    user_name = pytest.configs.get_config("lynx_enabled_rt_provider")
    password = pytest.configs.get_config("all_provider_password")
    doctor_id = pytest.configs.get_config("lynx_enabled_rt_provider_id")
    ehr_enabled_doctor = pytest.configs.get_config('ehr_lynx_enabled_rt_provider')
    ehr_enabled_doctor_id = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_id')
    date_time_pattern = r'\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}.?([0-9]*)'
    stream_id = ''
    second_appointment_id = ''
    second_note_id = ''
    ehr_enabled_note_stream_id = ''
    ehr_enabled_note_id = ''
    #headers = ''


    def setup_class(self):
        self.transcript_page = TranscriptApiPage()
        self.data = Data()
        self.db = DB()
        self.appointments_page = AppointmentsApiPage()
        self.authorization_page = AuthorizationApiPage()
        self.ehr_upload_page = EHRUploadApiPage()
        response_data, self.token, self.headers, self.note_id = self.appointments_page.create_and_authorize_a_non_ehr_appointment(user_name=self.user_name,
                                                                                                                    password=self.password,
                                                                                                                    doctor_id=self.doctor_id)

        # Get ehr enabled provider auth token
        self.ehr_enabled_token = RequestHandler.get_auth_token(user_name=self.ehr_enabled_doctor, password=self.password)

        self.transcript_path = self.note_id
        # Upload an audio to note
        TestTranscript.stream_id = upload_audio_to_go_note(auth_token=self.token, note_id=self.note_id, file_path='utils/upload_go_audio/Visit8-v6_20221212.mp4')



    """ @pytest.fixture
    def setup_testcase_for_specific_testcases(self):
        yield
        self.appointments_page.delete_appointment_note(appointment_id=TestTranscript.second_appointment_id, note_id=TestTranscript.second_note_id, headers=self.headers)

    def teardown_class(cls):
        cls.appointments_page.delete_appointment_note(appointment_id=cls.appointment_id, note_id=cls.note_id, headers=cls.headers) """


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_uploaded_recording_for_a_valid_note_id(self):
        # Call the transcript api to get recording
        second_stream_id = upload_audio_to_go_note(auth_token=self.token, note_id=self.note_id,
                                                           file_path='utils/upload_go_audio/conversation.mp4')

        response = self.transcript_page.get_transcript_api_response(request_path=self.transcript_path, stream_id=second_stream_id, headers=self.headers, token=self.token)
        stream_ids = [TestTranscript.stream_id, second_stream_id]
        durations = ['2:06','2:40']
        with allure.step('Proper datalist, status_code and reason should be returned for get recordings for a valid note'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            for i in range(len(json_response)):
                assert json_response[i]['id'] == stream_ids[i]
                assert json_response[i]['duration'] == durations[i]
                assert json_response[i]['asr_model'] == 'medical_conversation'
                assert re.fullmatch(self.date_time_pattern, json_response[i]['datetime'])
        with open('resources/json_data/recording_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None


    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_uploaded_recording_for_a_valid_ehr_enabled_note_id(self):
        response_data = self.ehr_upload_page.get_appointment(auth_token=self.ehr_enabled_token, doctor_id=self.ehr_enabled_doctor_id)
        TestTranscript.ehr_enabled_note_id = response_data['dataList'][0]['uuid']
        # Upload an audio to note
        stream_id = upload_audio_to_go_note(auth_token=self.ehr_enabled_token, note_id=TestTranscript.ehr_enabled_note_id, file_path='utils/upload_go_audio/Visit8-v6_20221212.mp4')
        TestTranscript.ehr_enabled_note_stream_id = stream_id
        # Call the transcript api to all recordings
        response = self.transcript_page.get_transcript_api_response(request_path=TestTranscript.ehr_enabled_note_id, stream_id=TestTranscript.ehr_enabled_note_stream_id, token=self.ehr_enabled_token)
        with allure.step('Proper datalist, status_code and reason should be returned for get recordings for a valid ehr enabled note'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            assert json_response[-1]['id'] == TestTranscript.ehr_enabled_note_stream_id
            assert json_response[-1]['duration'] == '2:06'
            assert json_response[-1]['asr_model'] == 'medical_conversation'
            assert re.fullmatch(self.date_time_pattern, json_response[-1]['datetime'])
        with open('resources/json_data/recording_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sanity
    def test_get_transcript_for_a_recording(self):
        request_path = f'{self.note_id}/{TestTranscript.stream_id}'
        start_time = time.time()
        while True:
            response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, headers=self.headers, token=self.token)
            if response.status_code == 200:
                break
            if time.time() - start_time > 120:
                print("Max time limit reached. Transcription took too long")
                break
            time.sleep(1)
        with open('resources/json_data/transcript_response.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
            expected_response['id'] = TestTranscript.stream_id
        with allure.step('Proper datalist, status_code and reason should be returned for get transcript of recording for a valid note'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            json_response_sorted = sorted(json.dumps(json_response, sort_keys=True))
            expected_response = sorted(json.dumps(expected_response, sort_keys=True))
            assert json_response_sorted == expected_response
        # Schema validation
        with open('resources/json_data/transcript_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sanity
    def test_get_transcript_for_a_recording_of_an_ehr_enabled_note(self):
        request_path = f'{TestTranscript.ehr_enabled_note_id}/{TestTranscript.ehr_enabled_note_stream_id}'
        start_time = time.time()
        while True:
            response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, token=self.ehr_enabled_token)
            if response.status_code == 200:
                break
            if time.time() - start_time > 120:
                print("Max time limit reached. Transcription took too long")
                break
            time.sleep(1)
        with open('resources/json_data/transcript_response.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
            expected_response['id'] = TestTranscript.ehr_enabled_note_stream_id
        with allure.step('Proper datalist, status_code and reason should be returned for get transcript of recording for a valid note'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            json_response_sorted = sorted(json.dumps(json_response, sort_keys=True))
            expected_response = sorted(json.dumps(expected_response, sort_keys=True))
            assert json_response_sorted == expected_response
        # Schema validation
        with open('resources/json_data/transcript_schema.json', 'r') as json_file:
            expected_schema = json.loads(json_file.read())
        with allure.step('json schema is validated'):
            assert validate(json_response, expected_schema) is None

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sanity
    #@pytest.mark.usefixtures("setup_testcase_for_specific_testcases")
    def test_should_not_get_transcript_for_a_recording_by_another_note_id(self):
        response_data, token, headers, note_id = self.appointments_page.create_and_authorize_a_non_ehr_appointment(auth_token=self.token,
                                                                                                                    doctor_id=self.doctor_id)
        TestTranscript.second_note_id = note_id
        request_path = f'{TestTranscript.second_note_id}/{TestTranscript.stream_id}'
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, headers=self.headers, token=self.token)
        with allure.step('Proper datalist, status_code and reason should be returned for get transcript of recording with another note'):
            assert response.status_code == 400
            assert response.reason == 'Bad Request'
            json_response = response.json()
            assert json_response['error'] == 'Note Id must match Stream Id'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    #@pytest.mark.usefixtures("setup_testcase_for_specific_testcases")
    def test_that_the_api_returns_an_error_message_when_the_recording_file_does_not_exist(self):
        response_data, token, headers, note_id = self.appointments_page.create_and_authorize_a_non_ehr_appointment(auth_token=self.token,
                                                                                                                    doctor_id=self.doctor_id)
        TestTranscript.second_note_id = note_id
        request_path = f'{note_id}'
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, headers=self.headers, token=self.token)
        with allure.step('Proper error message should be returned when the recording file does not exist'):
            assert response.status_code == 404
            assert response.reason == 'Not Found'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    #@pytest.mark.usefixtures("setup_testcase_for_specific_testcases")
    def test_get_proper_transcript_for_a_mp3_audio(self):
        mp3_file_path = 'utils/upload_go_audio/Visit8-v6_20221212.mp3'
        response_data, token, headers, note_id = self.appointments_page.create_and_authorize_a_non_ehr_appointment(auth_token=self.token,
                                                                                                                    doctor_id=self.doctor_id)
        TestTranscript.second_note_id = note_id
        # Upload a mp3 audio and get api response
        stream_id, response = self.transcript_page.upload_an_audio_file_and_get_transcription(token=self.token, headers=self.headers, note_id=TestTranscript.second_note_id, file_path=mp3_file_path)
        with open('resources/json_data/transcript_response.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
            expected_response['id'] = stream_id
        with allure.step('Proper datalist, status_code and reason should be returned for get transcription of a mp3 audio recording for a valid note'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            json_response_sorted = sorted(json.dumps(json_response, sort_keys=True))
            expected_response = sorted(json.dumps(expected_response, sort_keys=True))
            # Calculate the percentage similarity
            similarity = jsondiff.similarity(json_response_sorted, expected_response)
            assert similarity >= 0.9, "JSON files are not at least 90% similar"
            #assert json_response_sorted == expected_response

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    #@pytest.mark.usefixtures("setup_testcase_for_specific_testcases")
    def test_that_the_api_returns_an_error_message_when_upload_a_wav_audio_file(self):
        wav_audio_file_path = 'utils/upload_go_audio/Visit8-v6_20221212.wav'
        response_data, token, headers, note_id = self.appointments_page.create_and_authorize_a_non_ehr_appointment(auth_token=self.token,
                                                                                                                    doctor_id=self.doctor_id)
        TestTranscript.second_note_id = note_id
        # Upload an audio to note
        upload_audio_to_go_note(auth_token=self.token, note_id=TestTranscript.second_note_id, file_path=wav_audio_file_path)
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=TestTranscript.second_note_id, headers=self.headers, token=self.token)
        with allure.step('Proper error message should be returned when upload a wav audio file for transcription'):
            assert response.status_code == 404
            assert response.reason == 'Not Found'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    #@pytest.mark.usefixtures("setup_testcase_for_specific_testcases")
    def test_get_proper_transcript_for_a_7_minutes_length_audio(self):
        mp4_file_path = 'utils/upload_go_audio/medium_length7mnt.mp4'
        response_data, token, headers, note_id = self.appointments_page.create_and_authorize_a_non_ehr_appointment(auth_token=self.token,
                                                                                                                    doctor_id=self.doctor_id)
        TestTranscript.second_note_id = note_id
        # Upload a7 minutes audio and get api response
        stream_id, response = self.transcript_page.upload_an_audio_file_and_get_transcription(token=self.token, headers=self.headers, note_id=TestTranscript.second_note_id, file_path=mp4_file_path)
        with open('resources/json_data/transcript_response_for_7_mnts_audio.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
            expected_response['id'] = stream_id
        with allure.step('Proper datalist, status_code and reason should be returned for get transcription of a 7 minutes recording for a valid note'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            json_response_sorted = sorted(json.dumps(json_response, sort_keys=True))
            expected_response = sorted(json.dumps(expected_response, sort_keys=True))
            assert json_response_sorted == expected_response


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    #@pytest.mark.usefixtures("setup_testcase_for_specific_testcases")
    def test_get_proper_transcript_for_a_30_minutes_length_audio(self):
        mp4_file_path = 'utils/upload_go_audio/30_Plus_mnt.mp4'
        response_data, token, headers, note_id = self.appointments_page.create_and_authorize_a_non_ehr_appointment(auth_token=self.token,
                                                                                                                    doctor_id=self.doctor_id)
        TestTranscript.second_note_id = note_id
        # Upload a 30 minutes audio and get api response
        stream_id, response = self.transcript_page.upload_an_audio_file_and_get_transcription(token=self.token, headers=self.headers, note_id=TestTranscript.second_note_id, file_path=mp4_file_path)
        with open('resources/json_data/transcript_response_for_30_mnts_audio.json', 'r') as json_file:
            expected_response = json.loads(json_file.read())
            expected_response['id'] = stream_id
        with allure.step('Proper datalist, status_code and reason should be returned for get transcription of a 30 minutes recording for a valid note'):
            assert response.status_code == 200
            assert response.reason == 'OK'
            json_response = response.json()
            json_response_sorted = sorted(json.dumps(json_response, sort_keys=True))
            expected_response = sorted(json.dumps(expected_response, sort_keys=True))
            assert json_response_sorted == expected_response

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_should_not_get_transcript_for_a_recording_by_expired_auth_token(self):
        # Generate headers with expired auth token
        expired_token = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_expired_token')
        request_path = f'{self.note_id}/{TestTranscript.stream_id}'
        request_data = APIRequestDataHandler('authentication')
        headers_with_expired_token = request_data.get_modified_headers(Authorization=f'Bearer {expired_token}')
        # Call the transcript API to access the transcript of a recording with expired auth token
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, headers=headers_with_expired_token)
        with allure.step('Proper datalist, status_code and reason should be returned for get transcript of recording with expired auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_should_not_get_transcript_for_a_recording_by_invalid_auth_token(self):
        # Generate headers with invalid auth token
        invalid_token = pytest.configs.get_config('ehr_lynx_enabled_rt_provider_invalid_token')
        request_path = f'{self.note_id}/{TestTranscript.stream_id}'
        request_data = APIRequestDataHandler('authentication')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {invalid_token}')
        # Call the transcript API to access the transcript of a recording with expired auth token
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, headers=headers_with_invalid_token)
        with allure.step('Proper datalist, status_code and reason should be returned for get transcript of recording with invalid auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_should_not_get_transcript_for_a_recording_by_algorithm_set_as_none_token(self):
        # Generate headers with algorithm set as none token
        algorithm_none_token = pytest.configs.get_config('token_with_algorithm_set_as_none')
        request_path = f'{self.note_id}/{TestTranscript.stream_id}'
        request_data = APIRequestDataHandler('authentication')
        headers_with_invalid_token = request_data.get_modified_headers(Authorization=f'Bearer {algorithm_none_token}')
        # Call the transcript API to access the transcript of a recording with algorithm set as none auth token
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, headers=headers_with_invalid_token)
        with allure.step('Proper datalist, status_code and reason should be returned for get transcript of recording with algorithm set as none token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.usefixtures("setup_testcase_for_user_active_testcases")
    @pytest.mark.security
    def test_should_not_get_transcript_for_a_recording_by_recently_blocked_auth_token(self):
        request_path = f'{self.note_id}/{TestTranscript.stream_id}'
        auth_token = RequestHandler.get_auth_token(user_name=self.user_name, password=self.password)
        # Block the provider
        for _ in range(4):
            RequestHandler.get_auth_response(user_name=self.user_name, password='Augmedix@23')
        # Call the transcript API to access the transcript of a recording with recently blocked auth token
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, token=auth_token)
        with allure.step('Proper datalist, status_code and reason should be returned for get transcript of recording with recently blocked auth token'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_uploaded_recording_of_a_valid_note(self):
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=self.transcript_path, request_type="POST", headers=self.headers, token=self.token)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_uploaded_recording_of_a_valid_note(self):
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=self.transcript_path, request_type="PUT", headers=self.headers, token=self.token)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_uploaded_recording_of_a_valid_note(self):
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=self.transcript_path, request_type="PATCH", headers=self.headers, token=self.token)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_get_uploaded_recording_of_a_valid_note(self):
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=self.transcript_path, request_type="DELETE", headers=self.headers, token=self.token)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_method_should_not_support_for_get_transcription_of_a_recording(self):
        request_path = f'{self.note_id}/{TestTranscript.stream_id}'
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, request_type="POST", headers=self.headers, token=self.token)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'POST' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_method_should_not_support_for_get_transcription_of_a_recording(self):
        request_path = f'{self.note_id}/{TestTranscript.stream_id}'
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, request_type="PUT", headers=self.headers, token=self.token)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PUT' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_patch_method_should_not_support_for_get_transcription_of_a_recording(self):
        request_path = f'{self.note_id}/{TestTranscript.stream_id}'
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, request_type="PATCH", headers=self.headers, token=self.token)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'PATCH' not supported"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_method_should_not_support_for_get_transcription_of_a_recording(self):
        request_path = f'{self.note_id}/{TestTranscript.stream_id}'
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, request_type="DELETE", headers=self.headers, token=self.token)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 405
            assert response.reason == 'Method Not Allowed'
            json_response = response.json()
            assert json_response['status'] == 405
            assert json_response['error'] == 'Method Not Allowed'
            assert json_response['message'] == "Request method 'DELETE' not supported"

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_that_the_api_returns_an_error_message_when_try_to_get_uploaded_recording_info_for_a_empty_note_id(self):
        # Call the transcript api to get recording
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path="", request_type="GET", headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 404
            assert response.reason == 'Not Found'

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_that_the_api_returns_an_error_message_when_try_to_get_uploaded_recording_info_for_a_invalid_note_id(self):
        # Call the transcript api to get recording
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path="72d5c66b-14cc-4939-invalid", request_type="GET", headers=self.headers)
        with allure.step('Proper messages, status_code and reason should be returned'):
            assert response.status_code == 404
            assert response.reason == 'Not Found'

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_user_should_not_get_recording_info_for_another_user_note_id(self):
        response_data, token, headers, TestTranscript.second_note_id = self.appointments_page.create_and_authorize_a_non_ehr_appointment(auth_token=self.token,
                                                                                                                    doctor_id=self.doctor_id)
        request_path = TestTranscript.second_note_id
        response = RequestHandler.get_api_response(base_url=self.transcript_base_url, request_path=request_path, token=self.ehr_enabled_token)
        with allure.step('Proper datalist, status_code and reason should be returned for get recording info for_another_user_note_id'):
            assert response.status_code == 401
            assert response.reason == 'Unauthorized'
            json_response = response.json()
            assert json_response['message'] == 'Unauthorized'
