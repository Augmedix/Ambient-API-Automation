# pylint: disable=no-member, attribute-defined-outside-init
import json
import pytest
import time
from utils.request_handler import RequestHandler
from pages.base_page import BasePage
from utils.api_request_data_handler import APIRequestDataHandler


class RecordingProcessPage(BasePage):
    def __init__(self):
        """
        Initialize the RecordingProcessPage with API request data.
        """
        self.request_data = APIRequestDataHandler("recording_api")
        self.base_url = pytest.configs.get_config('recording_api_base_url')

    def create_recording_process(self, doctor_id, note_id, user_name=None, password=None, auth_token=None, payload=None):
        """
        Create a new recording process.
        """
        token = auth_token if auth_token else RequestHandler.get_auth_token(user_name=user_name, password=password)
        
        headers = self.request_data.get_modified_headers(Authorization=f'Bearer {token}')
        if not payload:
            payload = self.request_data.get_modified_payload(
                name='create_recording',
                doctorId=str(doctor_id),
                noteId=str(note_id),
            )

        updated_payload = json.dumps(payload, indent=4)
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path="recording/process",
            request_type="POST",
            headers=headers,
            payload=updated_payload
        )

        # Handle blank response with status code 200
        if response.status_code == 200 and not response.text.strip():
            print(f"Blank response received with status code 200 for create_recording_process.")
            return {"message": "Recording process created successfully", "status_code": 200}

        # Handle invalid JSON response
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response.text}, Status Code: {response.status_code}")

        return response_json

    def get_recording_process(self, note_id, user_name=None, password=None, auth_token=None, payload=None):
        """
        Retrieve details of a recording process by note ID.
        """
        token = auth_token if auth_token else RequestHandler.get_auth_token(user_name=user_name, password=password)
        
        headers = self.request_data.get_modified_headers(Authorization=f'Bearer {token}')
        path = f"recording/process?noteIds={note_id}"
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="GET",
            token=token,
            headers=headers
        )

        return response

    def update_recording_process(self, doctor_id, note_id, user_name=None, password=None, auth_token=None, payload=None):
        """
        Update (re-process) a recording process.
        """
        token = auth_token if auth_token else RequestHandler.get_auth_token(user_name=user_name, password=password)
        
        headers = self.request_data.get_modified_headers(Authorization=f'Bearer {token}')
        if not payload:
            payload = self.request_data.get_modified_payload(
                name='update_recording',
                doctorId=str(doctor_id),
                noteId=str(note_id),
            )
            for container in payload.get("recordingProcessContainers", []):
                container["recordingName"] = "Updated Recordings"  # Update the recordingName dynamically

        updated_payload = json.dumps(payload, indent=4)
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path="recording/process",
            request_type="PUT",
            token=token,
            headers=headers,
            payload=updated_payload
        )

        # Handle blank response with status code 200
        if response.status_code == 200 and not response.text.strip():
            print(f"Blank response received with status code 200 for update_recording_process.")
            return {"message": "Recording process updated successfully", "status_code": 200}

        # Handle invalid JSON response
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response.text}, Status Code: {response.status_code}")

        print(f"Update Recording Process Response: {response_json}, Status Code: {response.status_code}")
        return response_json

    def poll_status(self, note_id, user_name=None, password=None, auth_token=None, payload=None, max_retries=10, interval=5):
        """
        Poll the status of a recording process until it is COMPLETED or max retries are reached.
        """
        token = auth_token if auth_token else RequestHandler.get_auth_token(user_name=user_name, password=password)
        
        headers = self.request_data.get_modified_headers(Authorization=f'Bearer {token}')
        for attempt in range(max_retries):
            response = self.get_recording_process(note_id, auth_token=token)
            status = response.get("status")
            print(f"Polling attempt {attempt + 1}: Status = {status}")

            if status == "COMPLETED":
                print("Recording process completed.")
                return response
            elif status == "PROCESSING":
                print("Recording process is still processing. Retrying...")
                time.sleep(interval)
            else:
                raise AssertionError(f"Unexpected status: {status}")

        raise AssertionError("Recording process did not complete within the expected time.")