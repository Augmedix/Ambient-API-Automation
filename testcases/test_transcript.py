# pylint: disable=no-member, attribute-defined-outside-init
import requests
import json
import pytest
import allure
from pages.transcript_api_page import TranscriptApiPage
from pages.appointments_api_page import AppointmentsApiPage
from testcases.base_test import BaseTest
from utils.helper import validate_response_schema
import time


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
        self.user_name = pytest.configs.get_config('appointment_api_provider')
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

        # Print headers and token for debugging
        print(f"Headers: {self.headers}")
        print(f"Token: {self.token}")

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

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_transcript_with_invalid_token(self):
        """
        Test GET /transcript with an invalid token.
        """
        invalid_token = "Bearer invalid.token.example"
        response = self.transcript_page.get_transcript(self.stream_id, auth_token=invalid_token)
        response_json = response.json()
        print(f"Response: {response_json}")

        # Validate the response
        assert response.status_code == 403, "Expected 403 Forbidden for invalid token"
        assert response_json.get("error") == "User is not allowed.", "Expected 'User is not allowed.' in error message"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_note_list_with_missing_token(self):
        """
        Test POST /transcript/get_notelist with a missing token.
        """
        note_ids = [self.note_id]
        response = self.transcript_page.get_note_list(note_ids, auth_token=None)
        print(f"Response: {response}")

        # Validate the response
        assert response.status_code == 401, "Expected 401 Unauthorized for missing token"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_transcript_with_invalid_stream_id(self):
        """
        Test GET /transcript with an invalid stream ID.
        """
        invalid_stream_id = "invalid_stream_id"
        response = self.transcript_page.get_transcript(invalid_stream_id, auth_token=self.token)
        response_json = response.json()
        print(f"Response: {response_json}")

        # Validate the response
        assert response.status_code in [400, 404], "Expected 400 or 404 for invalid stream ID"
        assert "error" in response_json, "Expected 'error' in response JSON"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_note_list_with_invalid_note_id(self):
        """
        Test POST /transcript/get_notelist with an invalid note ID.
        """
        invalid_note_ids = ["invalid_note_id"]
        response = self.transcript_page.get_note_list(invalid_note_ids, auth_token=self.token)
        response_json = response.json()
        print(f"Response: {response_json}")

        # Validate the response
        assert response.status_code in [400, 404], "Expected 400 or 404 for invalid note ID"
        assert "error" in response_json, "Expected 'error' in response JSON"
