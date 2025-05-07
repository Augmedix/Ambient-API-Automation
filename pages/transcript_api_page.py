# pylint: disable=no-member, attribute-defined-outside-init
import json
import pytest
import time
from utils.request_handler import RequestHandler
from pages.base_page import BasePage
from utils.api_request_data_handler import APIRequestDataHandler
from pages.recording_process_page import RecordingProcessPage

class TranscriptApiPage(BasePage):
    def __init__(self):
        """
        Initialize the TranscriptApiPage with API request data.
        """
        self.recording_api_page = RecordingProcessPage()
        self.request_data = APIRequestDataHandler("transcript_api")
        self.base_url = pytest.configs.get_config("transcript_base_url")

    def post_recording_and_get_stream_id(self, doctor_id, note_id, auth_token, max_retries=15, interval=5):
        """
        Create a recording process and fetch the streamId from the response once it is not null or blank.
        """
        # Step 1: Create a recording process
        recording_response = self.recording_api_page.create_recording_process(
            doctor_id=doctor_id,
            note_id=note_id,
            auth_token=auth_token
        )
        print(f"Recording Process Response: {recording_response}")

        # Step 2: Validate the response
        if recording_response.get("status_code") != 200:
            raise ValueError(f"Failed to create recording process: {recording_response}")

        # Step 3: Poll the recording process until streamId is not null or blank
        for attempt in range(max_retries):
            response = self.recording_api_page.get_recording_process(
                note_id=note_id,
                auth_token=auth_token
            )
            print(f"Polling attempt {attempt + 1}: Recording Details: {response}")

            # Parse the response into JSON
            try:
                recording_details = response.json()
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON response: {response.text}")

            if isinstance(recording_details, list) and len(recording_details) > 0:
                recording_process = recording_details[0]
                recording_containers = recording_process.get("recordingProcessContainers", [])
                if len(recording_containers) > 0:
                    stream_id = recording_containers[0].get("streamId")
                    if stream_id:  # Check if streamId is not null or blank
                        print(f"Stream ID found: {stream_id}")
                        return stream_id

            print("Stream ID is still null or blank. Retrying...")
            time.sleep(interval)

        raise TimeoutError("Stream ID was not available within the expected time.")
    
    
    def upload_audio_to_go_note(self, auth_token, note_id, file_path):
        """
        Upload an audio file to a note and return the stream ID.
        """
        headers = self.request_data.get_modified_headers(Authorization=f"Bearer {auth_token}")
        payload = self.request_data.get_modified_payload(
            name="upload_audio",
            noteId=note_id,
            filePath=file_path,
        )
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path="audio/upload",
            request_type="POST",
            headers=headers,
            payload=json.dumps(payload),
        )

        # Handle invalid JSON response
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response.text}, Status Code: {response.status_code}")

        return response_json.get("streamId")

    def get_transcript(self, stream_id, auth_token):
        """
        Call GET /transcript API to retrieve transcript data.
        """
        headers = self.request_data.get_modified_headers(Authorization=f"Bearer {auth_token}")
        path = f"transcript?version=2&streamId={stream_id}"
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="GET",
            headers=headers,
        )

        return response

    def get_note_list(self, note_ids, auth_token):
        """
        Call POST /transcript/get_notelist API to retrieve note list.
        """
        headers = self.request_data.get_modified_headers(Authorization=f"Bearer {auth_token}")
        payload = json.dumps(note_ids)
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path="transcript/get_notelist",
            request_type="POST",
            headers=headers,
            payload=payload,
        )

        return response

    def poll_transcript_status(self, stream_id, auth_token, max_retries=10, interval=5):
        """
        Poll the status of a transcript until it is COMPLETED or max retries are reached.
        """
        headers = self.request_data.get_modified_headers(Authorization=f"Bearer {auth_token}")
        for attempt in range(max_retries):
            response = self.get_transcript(stream_id, auth_token=auth_token)
            response_json = response.json()
            status = response_json.get("status")
            print(f"Polling attempt {attempt + 1}: Status = {status}")

            if status == "COMPLETED":
                print("Transcript process completed.")
                return response_json
            elif status == "PROCESSING":
                print("Transcript process is still processing. Retrying...")
                time.sleep(interval)
            else:
                raise AssertionError(f"Unexpected status: {status}")

        raise AssertionError("Transcript process did not complete within the expected time.")