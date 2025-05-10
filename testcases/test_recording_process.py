# pylint: disable=no-member, attribute-defined-outside-init
import pytest
import time
import allure
import os
from utils.helper import validate_response_schema
from pages.recording_process_page import RecordingProcessPage
from testcases.base_test import BaseTest
from utils.request_handler import RequestHandler
from pages.appointments_api_page import AppointmentsApiPage


class TestRecordingProcess(BaseTest):
    def setup_class(self):
        """
        Authenticate and set up initial data for recording process tests.
        """
        self.recording_page = RecordingProcessPage()
        self.appointment_page = AppointmentsApiPage()
        self.user_name = pytest.configs.get_config('appointment_api_provider')
        self.password = pytest.configs.get_config("all_provider_password")
        # Retrieve the token from the environment variable
        self.token = os.environ.get('AUTH_TOKEN')
        if not self.token:
            raise ValueError("AUTH_TOKEN environment variable is not set.")

        (
            self.json_response,
            self.headers,
            self.note_id,
            self.patient_name,
            self.start_time_str,
            self.visit_end_time,
            self.response_body,
        ) = self.appointment_page.create_ambient_appointment(auth_token=self.token)
        
        # Get provider UID and construct recordingId
        self.provider_id = self.appointment_page.get_provider_Id(self.token)

        # Create a recording process for testing
        self.response_json = self.recording_page.create_recording_process(self.provider_id, self.note_id, auth_token=self.token)

    def teardown_class(self):
        """
        Clean up any test data created during the tests.
        """
        # self.recording_page.delete_recording_process(self.headers, self.recording_id)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_post_recording_process(self):
        """
        Test POST /recording/process to create a new recording process.
        """
        # Validate the response
        assert self.response_json.get("status_code") == 200, "POST /recording/process failed"
        validate_response_schema(self.response_json, "resources/json_schema/post_recording_process.json")

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_recording_process_with_invalid_token(self):
        """
        Test POST /recording/process with an invalid token.
        """
        invalid_token = "Bearer invalid.token.example"
        response = self.recording_page.create_recording_process(self.provider_id, self.note_id, auth_token=invalid_token)
        print(f"Response: {response}")

        # Validate the response
        assert response.get("status_code") == 401, f"Expected 401 Unauthorized, got {response.get('status_code')}"
        assert "error" in response, "Expected 'error' in response JSON"
        assert response.get("error") == "Unauthorized", "Expected 'Unauthorized' in error message"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_put_recording_process_reprocess(self):
        """
        Test PUT /recording/process to re-process a recording.
        """
        response = self.recording_page.update_recording_process(self.note_id, self.provider_id, auth_token=self.token)
        print(f"Response: {response}")

        # Validate the response
        assert response.get("status_code") == 200, "PUT /recording/process failed"
        validate_response_schema(response, "resources/json_schema/put_recording_process.json")

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_recording_process(self):
        """
        Test GET /recording/process to retrieve recording process details.
        """
        response = self.recording_page.get_recording_process(self.note_id, auth_token=self.token)
        print(f"Response: {response}")
        response_json = response.json()

        # Validate the response
        assert response.status_code == 200, "GET /recording/process failed"
        assert isinstance(response_json, list), "Response should be a list"
        validate_response_schema(response_json, "resources/json_schema/get_recording_process.json")

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_recording_process_with_missing_token(self):
        """
        Test GET /recording/process with a missing token.
        """
        response = self.recording_page.get_recording_process(self.note_id, auth_token=None)
        print(f"Response: {response}")

        # Validate the response
        assert response.get("status_code") == 401, f"Expected 401 Unauthorized, got {response.get('status_code')}"
        assert "error" in response, "Expected 'error' in response JSON"
        assert response.get("error") == "Unauthorized", "Expected 'Unauthorized' in error message"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_polling_status_processing_completed(self):
        """
        Test status polling logic for PROCESSING and COMPLETED states.
        """
        max_retries = 10
        for _ in range(max_retries):
            response = self.recording_page.get_recording_process(self.note_id, auth_token=self.token)
            print(f"Polling Response: {response}")
            response_json = response.json()
            print(f"Polling Response: {response_json}")

            assert response.status_code == 200, "GET /recording/process failed during polling"

            # Handle list response
            if isinstance(response_json, list):
                status = response_json[0].get("status")
            else:
                status = response_json.get("status")

            if status == "COMPLETED":
                print("Recording process completed.")
                break
            elif status == "PROCESSING":
                print("Recording process is still processing. Retrying...")
                time.sleep(5)
            else:
                raise AssertionError(f"Unexpected status: {status}")
        else:
            raise AssertionError("Recording process did not complete within the expected time.")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_recording_process_missing_required_fields(self):
        """
        Test POST /recording/process with missing required fields.
        """
        response = self.recording_page.create_recording_process(None, None, auth_token=self.token)
        print(f"Response: {response}")

        # Validate the response
        assert response.get("status_code") == 400, f"Expected 400 Bad Request, got {response.get('status_code')}"
        assert "error" in response, "Expected 'error' in response JSON"
        assert "Missing required fields" in response.get("error", ""), "Expected 'Missing required fields' in error message"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_recording_process_with_invalid_note_id(self):
        """
        Test GET /recording/process with an invalid note ID.
        """
        invalid_note_id = "invalid_note_id"
        response = self.recording_page.get_recording_process(invalid_note_id, auth_token=self.token)
        print(f"Response: {response}")

        # Validate the response
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_recording_process_with_invalid_data(self):
        """
        Test PUT /recording/process with invalid data.
        """
        invalid_provider_id = "invalid_provider_id"
        response = self.recording_page.update_recording_process(self.note_id, invalid_provider_id, auth_token=self.token)
        print(f"Response: {response}")

        # Validate the response
        assert response.get("status_code") in [400, 404], f"Expected 400 or 404, got {response.get('status_code')}"
        assert "error" in response, "Expected 'error' in response JSON"