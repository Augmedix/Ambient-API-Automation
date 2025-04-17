import json

import requests


def create_auth_payload(emailID, password):
    auth_body = {
        'userType': "docApp",
        'deviceTag': "RF8K21KJ8HJ",
        'username': emailID,
        'authType': "password",
        'password': password,
        'rootCheckEnabled': False,
        'debugCheckEnabled': False,
        'appCheckEnabled': False,
        'ipAddress': "0.0.0.0",
        'glassVersion': "SM-G965U",
        'versionCode': 96,
        'versionName': "1.0.24E NRT"
    }

    auth_payload = json.dumps(auth_body)
    return auth_payload

def send_auth_request(auth_server_url, payload):
    headers = {'Content-type': 'application/json'}
    token = ""

    response = requests.post(auth_server_url, data=payload, headers=headers)
    if response.ok:
        print(auth_server_url + " signal sent", len(payload))
        response_dict = json.loads(response.text)
        token = response_dict["token"]
    else:
        print(auth_server_url + " signal sending error:", response)

    return token

def get_auth_token(authURL, emailID, password):
    print("fetching auth token for: " + emailID)

    payload = create_auth_payload(emailID, password)
    print(payload)
    token = send_auth_request(authURL, payload)

    print("auth token: " + token)

    return token