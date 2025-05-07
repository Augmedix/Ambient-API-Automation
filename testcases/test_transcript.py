# pylint: disable=no-member, attribute-defined-outside-init
import requests
import json
import pytest
import allure
from pages.transcript_api_page import TranscriptApiPage
from pages.appointments_api_page import AppointmentsApiPage
from pages.authorization_api_page import AuthorizationApiPage
from pages.ehr_upload_api_page import EHRUploadApiPage
from testcases.base_test import BaseTest
from utils.helper import get_formatted_date_str, compare_date_str, validate_response_schema
from utils.request_handler import RequestHandler
import jwt
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
    
    stream_id = ''
    second_appointment_id = ''
    second_note_id = ''
    ehr_enabled_note_stream_id = ''
    ehr_enabled_note_id = ''

    def setup_class(self):
        """
        Set up initial data for Transcript tests.
        """
        self.transcript_page = TranscriptApiPage()
        self.appointments_page = AppointmentsApiPage()
        self.transcript_base_url = pytest.configs.get_config('transcript_base_url')
        self.date_time_pattern = r'\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}.?([0-9]*)'
        self.user_name = pytest.configs.get_config('appointment_api_provider') #("transcript_api_user")
        self.password = pytest.configs.get_config("all_provider_password")

        (
            self.json_response,
            self.token,
            self.headers,
            self.note_id,
            self.patient_name,
            self.start_time_str,
            self.visit_end_time,
            self.response_body,
        ) = self.appointments_page.create_ambient_appointment(self.user_name, self.password)
        
        # Get Doctor ID and construct recordingId
        self.doctor_id = self.appointments_page.get_provider_Id(self.token)

        # Post a recording and fetch the stream ID
        self.stream_id = self.transcript_page.post_recording_and_get_stream_id(
            doctor_id=self.doctor_id,
            note_id=self.note_id,
            auth_token=self.token
        )

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_transcript(self):
        """
        Test GET /transcript to retrieve transcript data.
        """
        response = self.transcript_page.get_transcript(self.stream_id, auth_token=self.token)
        response_json = response.json()
        print(f"Response: {response_json}")

        # Validate the response
        assert response.status_code == 200, "GET /transcript failed"
        validate_response_schema(response_json, "resources/json_schema/get_transcript.json")

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_note_list(self):
        """
        Test POST /transcript/get_notelist to retrieve note list.
        """
        note_ids = [self.note_id]
        response = self.transcript_page.get_note_list(note_ids, auth_token=self.token)
        response_json = response.json()
        print(f"Response: {response_json}")

        # Validate the response
        assert response.status_code == 200, "POST /transcript/get_notelist failed"
        validate_response_schema(response_json, "resources/json_schema/get_note_list.json")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_poll_transcript_status(self):
        """
        Test polling the status of the transcript until it is COMPLETED.
        """
        response = self.transcript_page.poll_transcript_status(
            stream_id=self.stream_id, auth_token=self.token, max_retries=10, interval=5
        )
        print(f"Final Polling Response: {response}")
        assert response.get("status") == "COMPLETED", "Transcript status did not reach COMPLETED"
