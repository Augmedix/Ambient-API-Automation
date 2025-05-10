# pylint: disable=no-member, attribute-defined-outside-init
import json
import pytest
from utils.request_handler import RequestHandler
from utils.api_request_data_handler import APIRequestDataHandler
from utils.helper import get_current_pst_time, get_formatted_date_str
import random
from utils.request_handler import RequestHandler
from pages.base_page import BasePage
from utils.upload_go_audio.upload_audio import upload_audio_to_go_note


class AudioContinuityPage(BasePage):

    def __init__(self):
        self.request_data = APIRequestDataHandler('audio_continuity')
        #super().__init__()

    base_url = pytest.configs.get_config('audio_continuity_base_url')
    
    def post_audio(self, note_id, recording_id, user_name=None, password=None, auth_token=None, payload=None):
        """
        Sends a POST request to /audiocontinuity/v1/audios using the payload loaded from the JSON file,
        and replaces the recordingId with the provided note_id.
        """
        token = auth_token if auth_token else RequestHandler.get_auth_token(user_name=user_name, password=password)
        
        headers = self.request_data.get_modified_headers(Authorization=f'Bearer {token}')
       
        # Prepare payload
        if not payload:
            payload = self.request_data.get_modified_payload(
                name='post_audio',
                noteId=str(note_id),
                recordingId=str(recording_id),
            )

        updated_payload = json.dumps(payload, indent=4)
        

        # Prepare the path for the API request
        path = "audio"

        # Send the POST request with the updated payload
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="POST",
            headers=headers,
            token=token,
            payload=updated_payload  # Ensure payload is JSON string
        )
        return response


    def put_audio(self, headers, token, note_id, payload=None):
        """
        Sends a PUT request to /audiocontinuity/v1/audios to update audio metadata using the payload
        loaded from the JSON file, and replaces the recordingId with the provided note_id.
        """
        # Load the initial payload from the audio_continuity.json file if not provided
        payload = self.request_data.get_modified_payload('put_audio') if not payload else payload

        # Dynamically update the recordingId in the payload with the note_id
        payload['recordingId'] = note_id

        # Prepare the path for the API request
        path = "audio"

        # Send the PUT request with the updated payload
        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="PUT",
            headers=headers,
            token=token,
            payload=json.dumps(payload)  # Ensure payload is JSON string
        )

        return response

    def get_audio_by_unique_id(self, headers, token, unique_id):
        path = f"audios/{unique_id}"
        return RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="GET",
            headers=headers,
            token=token
        )
    
    def get_audio_by_note_id(self, headers, token, note_id):
        path = f"audios/{note_id}"
        return RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="GET",
            headers=headers,
            token=token
        )
    
    def get_audio_by_provider_id(self, headers, token, provider_id):
        path = f"audios/{provider_id}"
        print(f"headers: {headers}")
        print(f"token: {token}")
        return RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="GET",
            headers=headers,
            token=token
        )

    def get_audio_by_provider_email(self, headers, token, email):
        path = f"audios/email/{email}"
        return RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="GET",
            headers=headers,
            token=token
        )

    def get_audio_by_recording_id(self, headers, token, recording_id):
        path = f"audios/{recording_id}"
        return RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type="GET",
            headers=headers,
            token=token
        )
