import json

import pytest
import requests
from requests.structures import CaseInsensitiveDict

import utils.trainer_portal_schedule_note.schedule_note as schedule_note
from utils.note_checking_and_deleting.get_auth_token import get_auth_token


def get_trainer_portal_auth_and_schedule_note(admin_email, password, paired_scribe_id):
    print(admin_email)
    print(password)
    print(paired_scribe_id)
    # trainer_portal_auth = pytest.configs.get_config('trainer_portal_auth')
    # print(trainer_portal_auth)
    api_base_url = pytest.configs.get_config('api_base_url')
    api_auth_url = pytest.configs.get_config('auth_url')
    url = f"{api_base_url}/{api_auth_url}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
    headers["Accept-Language"] = "en-US,en;q=0.9"
    headers["Cache-Control"] = "no-cache"
    headers["Connection"] = "keep-alive"
    headers["Content-Type"] = "application/json; charset=UTF-8"

    data = f'{{"username":"{admin_email}","password":"{password}","userType":"admin"}}'

    resp = requests.post(url, headers=headers, data=data)

    print(resp.text)
    response_dict = json.loads(resp.text)
    token = response_dict["token"]
    print(token)
    schedule_status = schedule_note.schedule_note_for_scribe(token, paired_scribe_id)

    return schedule_status


if __name__ == "__main__":
    get_trainer_portal_auth_and_schedule_note()
