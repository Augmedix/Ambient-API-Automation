import pytest
import requests


def send_request(token, email):
    api_base_url = pytest.configs.get_config('api_base_url')
    provider_service = pytest.configs.get_config('provider_service')
    url = f"{api_base_url}/{provider_service}/providers/me/settings?deviceVersionName=7.4.30E%20SP4%20Dev&deviceTag=unknown&deviceVersionCode=7261&email={email}&="
    print(url)
    payload = {}
    headers = {
        'Authorization': f'Bearer {token}',
        'x-goog-device-info-serial-number': 'unknown',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)

    print(response.text)
    return response.text
