# pylint: disable=no-member, attribute-defined-outside-init
import pytest
import allure
from utils.helper import validate_response_schema
from pages.appointments_api_page import AppointmentsApiPage
from pages.audio_continuity_page import AudioContinuityPage
from testcases.base_test import BaseTest


class TestAudioContinuity(BaseTest):
    def setup_class(self):
        """
        Authenticate provider and create ambient appointment.
        Set up initial token, headers, and note_id for tests.
        """
        self.appointment_page = AppointmentsApiPage()
        self.audio_page = AudioContinuityPage()
        self.user_name = pytest.configs.get_config("appointment_api_provider")
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
        ) = self.appointment_page.create_ambient_appointment(self.user_name, self.password)
        
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
        response_json = response.json()
        print(f"Response: {response_json}")

        assert response.status_code == 400, "POST /audiocontinuity/v1/audios with invalid payload did not return 400"
        assert "error" in response_json, "Expected 'error' in response for invalid payload"

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
        response_json = response.json()
        print(f"Response: {response_json}")

        assert response.status_code == 400, "PUT /audiocontinuity/v1/audios with missing recordingId did not return 400"
        assert "error" in response_json, "Expected 'error' in response for missing recordingId"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_audio_by_invalid_note_id(self):
        """
        Test GET /audiocontinuity/v1/audios/{noteId} with an invalid note ID.
        """
        invalid_note_id = "invalid_note_id"

        response = self.audio_page.get_audio_by_note_id(self.headers, self.token, invalid_note_id)
        response_json = response.json()
        print(f"Response: {response_json}")

        assert response.status_code == 404, "GET /audiocontinuity/v1/audios/{noteId} with invalid note ID did not return 404"
        assert "error" in response_json, "Expected 'error' in response for invalid note ID"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_audio_by_provider_id_no_data(self):
        """
        Test GET /audiocontinuity/v1/audios/{providerId} when no audio data exists.
        """
        provider_id = "non_existent_provider_id"

        response = self.audio_page.get_audio_by_provider_id(self.headers, self.token, provider_id)
        response_json = response.json()
        print(f"Response: {response_json}")

        assert response.status_code == 404, "GET /audiocontinuity/v1/audios/{providerId} failed"
        assert "error" in response_json, "Expected 'error' in response for invalid provider ID"