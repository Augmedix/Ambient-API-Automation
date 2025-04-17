import json

import pytest
import requests
from utils.s2t_handler import S2THandler


def get_auth_token(username, password):
    token = S2THandler.get_auth_token(username, password)
    # api_base_url = pytest.configs.get_config('api_base_url')
    # url = f"{api_base_url}/auth/v1/token?grantType=password&idp=com.augmedix.legacy"
    #
    # payload = json.dumps({
    #     "username": username,
    #     "password": password,
    #     "otp": "",
    #     "userType": "scribe"
    # })
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    #
    # response = requests.post(url, headers=headers, data=payload)
    #
    # print(response.json())

    return token
