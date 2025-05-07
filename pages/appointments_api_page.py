# pylint: disable=no-member
from datetime import datetime, timedelta
import json
import random
import uuid

import jwt
import pytest
from jwt import DecodeError

from pages.base_page import BasePage
from utils.api_request_data_handler import APIRequestDataHandler
from utils.helper import get_formatted_date_str, get_iso_formatted_datetime_str, get_current_pst_time_and_date
from utils.request_handler import RequestHandler
from pages.authorization_api_page import AuthorizationApiPage


class AppointmentsApiPage(BasePage):
    def __init__(self):
        self.authorization_page = AuthorizationApiPage()
        self.base_url = "https://dev-api2.augmedix.com"

    def create_ambient_appointment(self, user_name=None, password=None, payload=None, auth_token=None):
        """
        Create a new patient note (appointment).
        """
        token = auth_token if auth_token else RequestHandler.get_auth_token(user_name=user_name, password=password)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if not payload:
            payload = {
                "patientName": "Test Patient",
                "startTime": "10:00:00",
                "visitDate": "2025-03-28"
            }

        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path="note/v1/provider/patients",
            request_type="POST",
            headers=headers,
            payload=payload
        )

        try:
            response_json = response.json()
        except ValueError:
            # Handle non-JSON responses
            response_json = {"error": response.text}

        return (
            response_json,
            token,
            headers,
            response_json.get("noteId"),
            response_json.get("patientName"),
            response_json.get("visitStartTime"),
            response_json.get("visitEndTime"),
            response
        )

    def get_notes_by_visit_date(self, user_name, password, visit_date):
        """
        Get a list of notes for a specific visit date.
        """
        token = RequestHandler.get_auth_token(user_name=user_name, password=password)
        headers = {
            "Authorization": f"Bearer {token}"
        }
        path = f"note/v1/provider/patients?visitDate={visit_date}"

        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="GET",
            headers=headers
        )
        return response

    def update_note(self, note_id, payload, headers):
        """
        Update a note using the PATCH API.
        """
        path = f"note/v1/provider/patients/{note_id}"
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="PATCH",
            headers=headers,
            payload=payload
        )

        try:
            response_json = response.json()
        except ValueError:
            # Handle non-JSON responses
            response_json = {"error": response.text}

        return response, response_json

    def update_note_status_internal(self, note_id, note_status, headers):
        """
        Update the note status using the internal API.
        """
        path = f"note/v1/open/internal/provider/patients?noteId={note_id}&noteStatus={note_status}"
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="PATCH",
            headers=headers
        )
        return response

    def delete_appointment_note(self, appointment_id, note_id, headers):
        """
        Delete a specific appointment note.
        """
        path = f"note/v1/provider/patients/{note_id}"
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="DELETE",
            headers=headers
        )
        return response

    def create_and_authorize_a_non_ehr_appointment(self, user_name=None, password=None, auth_token=None):
        """
        Create and authorize a non-EHR appointment.
        """
        response_data, token, headers, note_id, patient_name, start_time, end_time, response = self.create_ambient_appointment(
            user_name=user_name,
            password=password,
            auth_token=auth_token
        )
        # Authorize the newly created note
        self.authorization_page.create_resource(auth_token=token, note_id=note_id)
        return response_data, token, headers, note_id
    

    def get_provider_Id(self, token: str) -> str:
        """
        Decode the JWT token and extract the provider's UID (provider ID).
        """
        decoded = jwt.decode(token, options={"verify_signature": False})
        doc_id = decoded.get("uid")

        if doc_id:
            print("Provider Id: ", doc_id)
            return doc_id
        else:
            raise ValueError("Provider ID (uid) not found in token")
        

    def get_provider_guid(self, token: str) -> str:
        """
        Decode the JWT token and extract the provider's UID (provider ID).
        """
        decoded = jwt.decode(token, options={"verify_signature": False})
        doc_id = decoded.get("guid")

        if doc_id:
            print("Provider guid: ", doc_id)
            return doc_id
        else:
            raise ValueError("Provider ID (guid) not found in token")



