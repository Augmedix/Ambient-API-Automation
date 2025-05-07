# pylint: disable=no-member
import json
import pytest
import allure
import re

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
    appointment_id = ''
    headers = ''

    def setup_class(self):
        self.appointment = AppointmentsApiPage()
        self.modification_date = get_formatted_date_str(_date_format='%Y-%m-%d')
        self.service_date = get_formatted_date_str(_days=2, _date_format='%Y-%m-%d')
        self.service_date_range_start = get_formatted_date_str(_days=1, _date_format='%Y-%m-%d')
        self.service_date_range_end = get_formatted_date_str(_days=3, _date_format='%Y-%m-%d')
        self.start_time_str, self.visit_date, self.start_time_dt = get_current_pst_time_and_date()

    def teardown_method(self):
        if self.appointment_id:
            self.appointment.delete_appointment_note(
                appointment_id=self.appointment_id,
                note_id=self.appointment_id,
                headers=self.headers
            )

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_create_patient_with_valid_required_fields_and_token(self):
        json_response, token, headers, note_id, patient_name, start_time_str, visit_end_time, response_body = \
            self.appointment.create_ambient_appointment(
                user_name=pytest.configs.get_config("appointment_api_provider"),
                password=pytest.configs.get_config("all_provider_password")
            )

        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code == 200
            assert response_body.reason == 'OK'
            assert json_response.get('noteId') == note_id
            assert json_response.get('patientName') == patient_name
            assert json_response.get('status') == "Scheduled"
            assert json_response.get('visitStartTime') == start_time_str
            assert json_response.get('visitEndTime') == visit_end_time

            with allure.step('JSON schema is validated'):
                validate_response_schema(json_response, self.schema_path)

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.negative
    def test_create_patient_note_missing_required_field(self):
        payload = {
            "patientName": "Test Patient",
            "startTime": "10:00:00"
        }

        json_response, token, headers, note_id, patient_name, start_time_str, visit_end_time, response_body = \
            self.appointment.create_ambient_appointment(
                user_name=pytest.configs.get_config("appointment_api_provider"),
                password=pytest.configs.get_config("all_provider_password"),
                payload=payload
            )

        with allure.step('Proper dataset, status_code and reason should be returned'):
            assert response_body.status_code in [400, 422], f"Expected 400/422, got {response_body.status_code}"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_create_patient_note_with_invalid_token(self):
        """
        Test creating a patient note with an invalid token.
        """
        invalid_token = "Bearer invalid.token.example"
        json_response, _, _, _, _, _, _, response_body = self.appointment.create_ambient_appointment(
            auth_token=invalid_token
        )

        with allure.step('Invalid token should return 401 Unauthorized'):
            assert response_body.status_code == 401, f"Expected 401 Unauthorized, got {response_body.status_code}"
            assert "error" in json_response, "Expected 'error' in response JSON"
            assert "Unauthorized" in json_response["error"], "Expected 'Unauthorized' in error message"

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.sanity
    def test_get_note_list_with_valid_date(self):
        response = self.appointment.get_notes_by_visit_date(
            user_name=pytest.configs.get_config("appointment_api_provider"),
            password=pytest.configs.get_config("all_provider_password"),
            visit_date=self.visit_date
        )

        with allure.step('Valid token and date should return status 200 and a list of notes'):
            assert response.status_code == 200
            assert response.reason == 'OK'

            response_json = response.json()
            assert isinstance(response_json, list)

            with allure.step('JSON schema is validated'):
                validate_response_schema(response_json, 'resources/json_schema/get_note_list_schema.json')

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_update_note_with_valid_fields(self):
        """
        Test PATCH /note/v1/provider/patients/{noteId} to update a note with valid fields.
        """
        note_id = self.appointment_id  # Assuming a valid note ID is available
        payload = {
            "status": "Cancelled",
            "patientName": "Updated Patient Name",
            "startTime": "15:00:00",
            "mode": "AMBIENT"
        }
        response = self.appointment.update_note(
            note_id=note_id,
            payload=payload,
            headers=self.headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Validate the response
        assert response.status_code == 200, "Expected 200 OK for valid note update"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_update_note_with_invalid_fields(self):
        """
        Test PATCH /note/v1/provider/patients/{noteId} to update a note with invalid fields.
        """
        note_id = self.appointment_id  # Assuming a valid note ID is available
        payload = {
            "status": "InvalidStatus",  # Invalid status
            "startTime": "invalid_time"  # Invalid time format
        }
        response, response_json = self.appointment.update_note(
            note_id=note_id,
            payload=payload,
            headers=self.headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Validate the response
        assert response.status_code == 401, "Expected 401 Unauthorized for invalid fields"
        assert "error" in response_json, "Expected 'error' in response JSON"
        assert "Unauthorized" in response_json["error"], "Expected 'Unauthorized' in error message"

    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.sanity
    def test_internal_update_note_status_with_valid_params(self):
        """
        Test PATCH /note/v1/open/internal/provider/patients to update note status with valid parameters.
        """
        note_id = self.appointment_id  # Assuming a valid note ID is available
        note_status = "Note Ready"
        response = self.appointment.update_note_status_internal(
            note_id=note_id,
            note_status=note_status,
            headers={"Authorization": "Basic <valid_basic_auth_token>"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Validate the response
        assert response.status_code == 200, "Expected 200 OK for valid note status update"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_internal_update_note_status_with_invalid_params(self):
        """
        Test PATCH /note/v1/open/internal/provider/patients to update note status with invalid parameters.
        """
        note_id = "invalid_note_id"  # Invalid note ID
        note_status = "InvalidStatus"  # Invalid status
        response = self.appointment.update_note_status_internal(
            note_id=note_id,
            note_status=note_status,
            headers={"Authorization": "Basic <valid_basic_auth_token>"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Validate the response
        assert response.status_code == 500, "Expected 500 Internal Server Error for invalid parameters"
        response_json = response.json()
        assert response_json["status"] == 500, "Expected status 500 in the response"
        assert response_json["error"] == "Internal Server Error", "Expected 'Internal Server Error' in the response"
        assert "Invalid token" in response_json["message"], "Expected 'Invalid token' in error message"

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_get_note_list_with_invalid_date(self):
        """
        Test GET /note/v1/provider/patients with an invalid visit date.
        """
        invalid_visit_date = "invalid_date"  # Invalid date format
        response = self.appointment.get_notes_by_visit_date(
            user_name=pytest.configs.get_config("appointment_api_provider"),
            password=pytest.configs.get_config("all_provider_password"),
            visit_date=invalid_visit_date
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Validate the response
        assert response.status_code == 500, "Expected 500 Internal Server Error for invalid visit date"
        response_json = response.json()
        assert response_json["status"] == 500, "Expected status 500 in the response"
        assert response_json["error"] == "Internal Server Error", "Expected 'Internal Server Error' in the response"
        assert "Unparseable date" in response_json["message"], "Expected 'Unparseable date' in error message"
