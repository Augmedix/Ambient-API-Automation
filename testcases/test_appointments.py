# pylint: disable=no-member
import json
import pytest
import allure
import re
import random
import os
from resources.data import Data
from testcases.base_test import BaseTest
from utils.api_request_data_handler import APIRequestDataHandler
from utils.dbConfig import DB
from utils.request_handler import RequestHandler
from utils.helper import (
    get_formatted_date_str,
    get_current_pst_time_and_date,
    validate_response_schema
)
from pages.appointments_api_page import AppointmentsApiPage


class TestAppointments(BaseTest):
    base_url = pytest.configs.get_config('appointments_base_url')
    schema_path = "resources/json_schema/generated_patient_note_response_schema.json"
    date_time_pattern = r'\\d{4}-\\d{2}-\\d{2}[T]\\d{2}:\\d{2}:\\d{2}.?([0-9]*)Z'


    def setup_class(self):
        self.appointment = AppointmentsApiPage()
        self.modification_date = get_formatted_date_str(_date_format='%Y-%m-%d')
        self.service_date = get_formatted_date_str(_days=2, _date_format='%Y-%m-%d')
        self.service_date_range_start = get_formatted_date_str(_days=1, _date_format='%Y-%m-%d')
        self.service_date_range_end = get_formatted_date_str(_days=3, _date_format='%Y-%m-%d')
        self.start_time_str, self.visit_date, self.start_time_dt = get_current_pst_time_and_date()
        # Retrieve the token from the environment variable
        self.token = os.environ.get('AUTH_TOKEN')
        if not self.token:
            raise ValueError("AUTH_TOKEN environment variable is not set.")
        
        self.json_response, self.headers, self.note_id, self.patient_name, self.start_time_str, self.visit_end_time, self.response_body = \
            self.appointment.create_ambient_appointment(
                auth_token=self.token,

            )


    """ def teardown_method(self):
        if self.appointment_id:
            self.appointment.delete_appointment_note(
                note_id=self.note_id,
                auth_token=self.token,
            ) """

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_create_patient_with_valid_required_fields_and_token(self):
        """
        Test creating a patient note with valid required fields and a valid token.
        """
        
        
        print(f"Status Code: {self.response_body.status_code}")
        print(f"Response Text: {self.response_body.text}")

        # Validate the response
        assert self.response_body.status_code == 200, f"Expected 200 OK, got {self.response_body.status_code}"
        assert self.json_response.get("noteId") == self.note_id, "Expected noteId in response"
        assert self.json_response.get("patientName") == self.patient_name, "Expected patientName in response"
        assert self.json_response.get("status") == "Scheduled", "Expected status 'Scheduled' in response"

        with allure.step('JSON schema is validated'):
            validate_response_schema(self.json_response, self.schema_path)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.negative
    def test_create_patient_note_missing_required_field(self):
        payload = {
            "patientName": "Test Patient",
            "startTime": "10:00:00"
        }

        json_response, token, headers, note_id, patient_name, start_time_str, visit_end_time, response_body = \
            self.appointment.create_ambient_appointment(
                auth_token=self.token,
                payload=payload
            )

        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code in [400, 422], f"Expected 400/422, got {response_body.status_code}"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_create_patient_note_missing_token(self):
        """
        Test creating a patient note without providing an authentication token.
        """
        payload = {
            "patientName": "Test Patient",
            "startTime": "10:00:00",
            "visitDate": self.visit_date
        }

        response_json, _, _, _, _, _, _, response_body = self.appointment.create_ambient_appointment(
            auth_token=None,
            payload=payload
        )

        print(f"Status Code: {response_body.status_code}")
        print(f"Response Body: {response_body.text}")

        # Validate the response
        assert response_body.status_code == 401, f"Expected 401 Unauthorized, got {response_body.status_code}"
        if response_json:
            error_message = response_json.get("error", "")
            print(f"Error Message: {error_message}")
            assert error_message, "Expected 'error' field in response JSON to be non-empty"
            assert "Unauthorized" in error_message, f"Expected 'Unauthorized' in error message, got '{error_message}'"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_patient_note_with_invalid_token(self):
        """
        Test creating a patient note with an invalid token.
        """
        invalid_token = "Bearer invalid.token.example"
        json_response, _, _, _, _, _, response_body = self.appointment.create_ambient_appointment(
            auth_token=invalid_token
        )

        with allure.step('Invalid token should return 401 Unauthorized'):
            assert response_body.status_code == 401, f"Expected 401 Unauthorized, got {response_body.status_code}"
            assert "error" in json_response, "Expected 'error' in response JSON"
            assert "Unauthorized" in json_response["error"], "Expected 'Unauthorized' in error message"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_create_patient_note_with_invalid_date_format(self):
        """
        Test creating a patient note with an invalid date format.
        """
        payload = {
            "patientName": "Test Patient",
            "startTime": "10:00:00",
            "visitDate": "invalid_date"
        }

        response_json, token, headers, note_id, patient_name, start_time_str, visit_end_time, response_body = \
            self.appointment.create_ambient_appointment(
                auth_token=self.token,
                payload=payload
            )

        print(f"Status Code: {response_body.status_code}")
        print(f"Response Body: {response_body.text}")

        # Validate the response
        assert response_body.status_code in [400, 500], f"Expected 400 or 500, got {response_body.status_code}"
        if response_body.status_code == 500:
            assert "Text 'invalid_date' could not be parsed" in response_body.text, "Expected parsing error message"

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_note_list_with_valid_date(self):
        """
        Test GET /note/v1/provider/patients with a valid visit date.
        """
        response_json, token, headers, response = self.appointment.get_notes_by_visit_date(
            auth_token=self.token,
            visit_date=self.visit_date
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Validate the response
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert isinstance(response_json, list), "Expected response to be a list"

        with allure.step('JSON schema is validated'):
            validate_response_schema(response_json, 'resources/json_schema/get_note_list_schema.json')

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_update_note_with_valid_fields(self):
        """
        Test PATCH /note/v1/provider/patients/{noteId} to update a note with valid fields.
        """
        payload = {
            "status": "Cancelled",
            "patientName": "Updated Patient Name",
            "startTime": "15:00:00",
            "mode": "AMBIENT"
        }
        print(f"Payload: {payload}")
        response_json, token, headers, response = self.appointment.update_note(
            note_id=self.note_id,
            payload=payload,
            auth_token=self.token
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Validate the response
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_update_note_with_invalid_fields(self):
        """
        Test PATCH /note/v1/provider/patients/{noteId} to update a note with invalid fields.
        """
        payload = {
            "status": "InvalidStatus",  # Invalid status
            "startTime": "invalid_time"  # Invalid time format
        }

        response_json, token, headers, response = self.appointment.update_note(
            note_id=self.note_id,
            payload=payload,
            auth_token=self.token
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 500, f"Expected 500, got {response.status_code}"
        assert "Text 'invalid_time' could not be parsed" in response.text, "Expected error message not found"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_update_note_missing_payload(self):
        """
        Test PATCH /note/v1/provider/patients/{noteId} to update a note without providing a payload.
        """
        response_json, token, headers, response = self.appointment.update_note(
            note_id=self.note_id,
            payload=None,
            auth_token=self.token
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}"
        if response.status_code == 200:
            print("Warning: API accepts requests without a payload.")

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_internal_update_note_status_with_valid_params(self):
        """
        Test PATCH /note/v1/open/internal/provider/patients to update note status with valid parameters.
        """
        note_status = "Note Ready"
        print(f"Headers: {self.headers}")
        print(f"Note ID: {self.note_id}")
        print(f"Token: {self.token}")

        response_json, token, headers, response = self.appointment.update_note_status_internal(
            note_id=self.note_id,
            note_status=note_status,
            auth_token=self.token,
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Validate the response
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert response_json.get("status") == "Note Ready", "Expected status to be 'Note Ready'"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_internal_update_note_status_with_invalid_params(self):
        """
        Test PATCH /note/v1/open/internal/provider/patients to update note status with invalid parameters.
        """
        note_id = "invalid_note_id"  # Invalid note ID
        note_status = "InvalidStatus"  # Invalid status

        response_json, token, headers, response = self.appointment.update_note_status_internal(
            note_id=note_id,
            note_status=note_status,
            auth_token=self.token,
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 500, f"Expected 500, got {response.status_code}"
        assert "Invalid token" in response.text, "Expected error message not found"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_note_list_with_invalid_date(self):
        """
        Test GET /note/v1/provider/patients with an invalid visit date.
        """
        invalid_visit_date = "invalid_date"  # Invalid date format

        response_json, token, headers, response = self.appointment.get_notes_by_visit_date(
            auth_token=self.token,
            visit_date=invalid_visit_date
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 500, f"Expected 500, got {response.status_code}"
        assert "Unparseable date" in response.text, "Expected error message not found"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_notes_with_invalid_token(self):
        """
        Test GET /note/v1/provider/patients with an invalid authentication token.
        """
        invalid_token = "Bearer invalid.token.example"

        response_json, token, headers, response = self.appointment.get_notes_by_visit_date(
            auth_token=invalid_token,
            visit_date=self.visit_date
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Validate the response
        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        if response_json:
            error_message = response_json.get("error", "")
            print(f"Error Message: {error_message}")
            assert error_message, "Expected 'error' field in response JSON to be non-empty"
            assert "Unauthorized" in error_message, f"Expected 'Unauthorized' in error message, got '{error_message}'"


