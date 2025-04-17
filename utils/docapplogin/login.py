import json

import pytest
import requests

import utils.docapplogin.provider_service as provider_settings


def get_auth_token_and_send_req():
    api_base_url = pytest.configs.get_config('api_base_url')
    api_auth_url = pytest.configs.get_config('auth_url')
    url = f"{api_base_url}/{api_auth_url}"
    print(url)
    print(pytest.configs.get_config('eod_provider'))
    payload = json.dumps({
        "userType": "docApp",
        "deviceTag": "Postman Test Device",
        "username": pytest.configs.get_config('eod_provider'),
        "authType": "password",
        "password": pytest.configs.get_config('password'),
        "rootCheckEnabled": False,
        "debugCheckEnabled": True,
        "appCheckEnabled": True,
        "ip_address": "192.168.68.117",
        "glassVersion": "SM-G965U1",
        "versionCode": 7260,
        "versionName": "7.4.33E SP4 Dev"
    })
    headers = {
        'Authorization': 'Bearer',
        'x-goog-device-info-serial-number': 'unknown',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    print(response.text)
    response_dict = json.loads(response.text)
    token = response_dict["token"]
    print(token)

    res = provider_settings.send_request(token, pytest.configs.get_config('eod_provider'))

    print("response is: " + res)


if __name__ == "__main__":
    get_auth_token_and_send_req()
