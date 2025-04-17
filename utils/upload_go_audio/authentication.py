import requests
import json
import pytest


def create_auth_payload(email_id, password):
    auth_body = {
        "userType": "docApp",
        "username": email_id,
        "password": password,
        "versionName": "1.1.19",
        "authType": "password",
        "glassVersion": "iPhone (iOS 16.2)",
        "rootCheckEnabled": False,
        "debugCheckEnabled": False,
        "appCheckEnabled": False,
        "versionCode": 20221238,
        "ip_address": "0.0.0.0",
        "deviceTag": "RF8K21KJ8HJ"
    }

    auth_payload = json.dumps(auth_body)
    return auth_payload


def send_auth_request(payload):
    headers = {'Content-type': 'application/json'}
    token = ""
    auth_server_url = pytest.configs.get_config('go_auth_url')
    response = requests.post(auth_server_url, data=payload, headers=headers)
    if response.ok:
        print(auth_server_url + " signal sent", len(payload))
        response_dict = json.loads(response.text)
        token = response_dict["token"]
    else:
        print(auth_server_url + " signal sending error:", response)

    return token

def get_auth_token(email_id, password):
    print("fetching auth token for: " + email_id)

    payload = create_auth_payload(email_id, password)
    token = send_auth_request(payload)

    print("auth token: " + token)

    return token
