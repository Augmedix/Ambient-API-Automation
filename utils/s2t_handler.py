import datetime
import json

import pytest
import requests

from utils.uploadscript import nrt_upload


class S2THandler:
    api_base_url = pytest.configs.get_config('api_base_url')
    auth_url = pytest.configs.get_config('auth_url')
    recording_url = pytest.configs.get_config('recording_url')
    provider_email = pytest.configs.get_config('s2t_provider')
    scribe_email = pytest.configs.get_config('s2t_scribe')
    password = pytest.configs.get_config('password')
    provider_id = pytest.configs.get_config('s2t_provider_id')

    @staticmethod
    def get_auth_token(username, password):
        url = f'{S2THandler.api_base_url}/{S2THandler.auth_url}'

        payload = json.dumps({
            "username": username,
            "password": password,
            "otp": "",
            "userType": "scribe"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)

        print(response.json())

        return response.json()['token']

    @staticmethod
    def upload_audio_for_note():
        with open('resources/recordings/s2t.rec') as _recording_file:
            recording_file_content = str(_recording_file.read())

        url = f'{S2THandler.api_base_url}/{S2THandler.recording_url}'

        payload = json.dumps({
            "recordingFile": recording_file_content,
            "recordingId": f"dictation_{S2THandler.provider_id}_1649245460443",
            "providerEmail": S2THandler.provider_email,
            "providerId": int(S2THandler.provider_id),
            "type": "dictation",
            "patientName": f"AutoPatient_{id(5)}",
            "recordingStartTime": f"{datetime.datetime.now()}"
        })

        print(S2THandler.scribe_email, S2THandler.password)
        token = S2THandler.get_auth_token(
            S2THandler.scribe_email, S2THandler.password)

        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)

        print(response)
        print('=' * 100)

    def upload_nrt_recording(self):
        upload_status = nrt_upload.nrt_api(pytest.configs.get_config('mcu_server'),
                                           pytest.configs.get_config('visit_type'),
                                           pytest.configs.get_config('recording_type'),
                                           pytest.configs.get_config('recording_file_path'),
                                           pytest.configs.get_config('doctor_email'),
                                           pytest.configs.get_config('doctor_pass'),
                                           pytest.configs.get_config('auth_url_nrt'),
                                           pytest.configs.get_config('note_creation_url'),
                                           pytest.configs.get_config('note_name'))

        print(upload_status[0][1])

        return upload_status[0][1]


