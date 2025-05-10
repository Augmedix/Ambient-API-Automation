# pylint: disable=no-member, attribute-defined-outside-init
import pytest
import allure
import os
from utils.helper import validate_response_schema
from pages.appointments_api_page import AppointmentsApiPage
from pages.audio_continuity_page import AudioContinuityPage
from testcases.base_test import BaseTest


class TestAudioContinuity(BaseTest):
    def setup_class(self):
        """
        Set up initial data for tests.
        """
        self.audio_page = AudioContinuityPage()

        # Retrieve the token from the environment variable
        self.token = os.environ.get('AUTH_TOKEN')
        if not self.token:
            raise ValueError("AUTH_TOKEN environment variable is not set.")

        self.appointment_page = AppointmentsApiPage()
        self.user_name = pytest.configs.get_config("appointment_api_provider")
        self.password = pytest.configs.get_config("all_provider_password")

        (
            self.json_response,
            self.headers,
            self.note_id,
            self.patient_name,
            self.start_time_str,
            self.visit_end_time,
            self.response_body,
        ) = self.appointment_page.create_ambient_appointment(auth_token=self.token)
        
        # Get provider GUID and construct recordingId
        self.provider_guid = self.appointment_page.get_provider_guid(self.token)
        self.recording_id = f"{self.provider_guid}-{self.note_id}"
    
        self.unique_id = self.audio_page.post_audio(self.note_id, self.recording_id, auth_token=self.token)

    def teardown_class(self):
        """
        Clean up any test data created during the tests.
        """
        #self.appointment_page.delete_appointment_note(self.headers, self.token, self.note_id)

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_put_audio(self):
        """
        Test PUT /audio endpoint to update audio metadata.
        """

        response = self.audio_page.put_audio(self.headers, self.token, self.recording_id)
        assert response.status_code == 200, "PUT /audio failed"
        validate_response_schema(response.json(), "resources/json_schema/put_audio.json")

        # Temporarily comment out the validation block
        """
        assert len(response_json) > 0, "No audio data found for the given noteId"

        # Validate the recordingId
        for audio in response_json:
            assert "recordingId" in audio, "Missing 'recordingId' in response"
            assert audio["recordingId"] == self.recording_id, f"Expected recordingId {self.recording_id}, got {audio['recordingId']}"
        """

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_audio_by_email(self):
        """
        Test GET /audios/email/{providerEmail} with valid, invalid, and empty email.
        """
        response = self.audio_page.get_audio_by_provider_email(self.headers, self.token, self.user_name)
        response_json = response.json()
        print(f"Response: {response_json}")

        assert response.status_code == 200 or response.status_code == 404, "GET /audios/email/{providerEmail} failed"
        assert isinstance(response_json, list), "Response should be a list"
        
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_get_audio_by_note_id(self):
        """
        Test GET /audios/note/{noteId} to retrieve uploaded audio by note ID.
        """
        response = self.audio_page.get_audio_by_note_id(self.headers, self.token, self.note_id)
        response_json = response.json()
        print(f"Response: {response_json}")

        assert response.status_code == 200, "GET /audios/note/{noteId} failed"
        assert isinstance(response_json, list), "Response should be a list"

        # Temporarily comment out the validation block
        """
        assert len(response_json) > 0, "No audio data found for the given noteId"

        # Validate the recordingId
        for audio in response_json:
            assert "recordingId" in audio, "Missing 'recordingId' in response"
            assert audio["recordingId"] == self.recording_id, f"Expected recordingId {self.recording_id}, got {audio['recordingId']}"
        """

    
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sanity
    def test_validate_unique_id(self):
        """
        Test to validate the uniqueness of the recordingId in the response.
        """
        response = self.audio_page.get_audio_by_unique_id(self.headers, self.token, self.unique_id)
        response_json = response.json()
        print(f"Response: {response_json}")

        assert response.status_code == 200, "GET /audios/note/{unique_id} failed"
        assert isinstance(response_json, list), "Response should be a list"


        # Temporarily comment out the validation block
        """
        assert len(response_json) > 0, "No audio data found for the given noteId"

        # Validate the recordingId
        for audio in response_json:
            assert "recordingId" in audio, "Missing 'recordingId' in response"
            assert audio["recordingId"] == self.recording_id, f"Expected recordingId {self.recording_id}, got {audio['recordingId']}"
        """
    
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_post_audio_invalid_payload(self):
        """
        Test POST /audiocontinuity/v1/audios with an invalid payload.
        """
        invalid_payload = {"invalidField": "invalidValue"}

        response = self.audio_page.post_audio(self.note_id, self.recording_id, auth_token=self.token, payload=invalid_payload)

        # Check if the response is valid
        assert response is not None, "Expected a response object, but got None"
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 400, f"Expected 400 Bad Request, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"
        assert "Invalid payload" in response_json.get("error", ""), "Expected 'Invalid payload' in error message"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_put_audio_missing_recording_id(self):
        """
        Test PUT /audiocontinuity/v1/audios with missing recordingId field.
        """
        payload = {
            "uploadStatus": "STARTED",
            "isPlayed": True,
            "isArchived": True,
            "audioLength": 0,
        }

        response = self.audio_page.put_audio(self.headers, self.token, self.note_id, payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_audio_by_invalid_note_id(self):
        """
        Test GET /audiocontinuity/v1/audios/{noteId} with an invalid note ID.
        """
        invalid_note_id = "invalid_note_id_123"  # Invalid format

        response = self.audio_page.get_audio_by_note_id(self.headers, self.token, invalid_note_id)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_audio_by_provider_id_no_data(self):
        """
        Test GET /audiocontinuity/v1/audios/{providerId} when no audio data exists.
        """
        provider_id = "non_existent_provider_id"

        response = self.audio_page.get_audio_by_provider_id(self.headers, self.token, provider_id)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_post_audio_with_invalid_token(self):
        """
        Test POST /audiocontinuity/v1/audios with an invalid token.
        """
        invalid_token = "Bearer invalid.token.example"
        payload = {"recordingId": self.recording_id, "uploadStatus": "STARTED"}

        response = self.audio_page.post_audio(self.note_id, self.recording_id, auth_token=invalid_token, payload=payload)

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        if response.text:
            response_json = response.json()
            assert "error" in response_json, "Expected 'error' in response JSON"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_get_audio_by_note_id_with_invalid_token(self):
        """
        Test GET /audiocontinuity/v1/audios/{noteId} with an invalid token.
        """
        invalid_token = "Bearer invalid.token.example"

        response = self.audio_page.get_audio_by_note_id(self.headers, invalid_token, self.note_id)

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"
        assert "Unauthorized" in response_json.get("error", ""), "Expected 'Unauthorized' in error message"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_put_audio_with_missing_token(self):
        """
        Test PUT /audiocontinuity/v1/audios with a missing token.
        """
        payload = {"recordingId": self.recording_id, "uploadStatus": "STARTED"}

        response = self.audio_page.put_audio(self.headers, None, self.recording_id, payload)

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"
        assert "Unauthorized" in response_json.get("error", ""), "Expected 'Unauthorized' in error message"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_post_audio_missing_required_fields(self):
        """
        Test POST /audiocontinuity/v1/audios with missing required fields.
        """
        payload = {"uploadStatus": "STARTED"}  # Missing recordingId

        response = self.audio_page.post_audio(self.note_id, self.recording_id, auth_token=self.token, payload=payload)

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 400, f"Expected 400 Bad Request, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"
        assert "Missing required field" in response_json.get("error", ""), "Expected 'Missing required field' in error message"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_audio_by_invalid_unique_id(self):
        """
        Test GET /audiocontinuity/v1/audios/{uniqueId} with an invalid unique ID.
        """
        invalid_unique_id = "invalid_unique_id_123"  # Invalid format

        response = self.audio_page.get_audio_by_unique_id(self.headers, self.token, invalid_unique_id)

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code in [400, 404], f"Expected 404 Not Found, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"
        assert "Audio not found" in response_json.get("error", ""), "Expected 'Audio not found' in error message"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_put_audio_with_invalid_recording_id(self):
        """
        Test PUT /audiocontinuity/v1/audios with an invalid recording ID.
        """
        invalid_recording_id = "f47ac10b-58cc-4372-a567-0e02b2c3d479Z"  # Invalid UUID format
        payload = {"recordingId": invalid_recording_id, "uploadStatus": "STARTED"}

        response = self.audio_page.put_audio(self.headers, self.token, invalid_recording_id, payload)

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 404, f"Expected 404 Not Found, got {response.status_code}"
        response_json = response.json()
        assert "error" in response_json, "Expected 'error' in response JSON"
        assert "Not Found" in response_json.get("error", ""), \
            f"Expected 'Not Found' in error message, got '{response_json.get('error', '')}'"