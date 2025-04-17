import json
import time

import pytest
import requests
from requests.structures import CaseInsensitiveDict


def check_if_transcription_processed(token, stream_id):

    url = f"{pytest.configs.get_config('transcription_process_check')}/streamsbystreamids"

    headers = CaseInsensitiveDict()
    headers[
        "Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = "application/json"
    headers["cache-control"] = "no-cache"

    data = f'{{ "streamIds": ["{stream_id}"]}}'

    print(data)

    for x in range(100):
        try:
            resp = requests.post(url, headers=headers, data=data)
            print(resp.json()[0]['media']['mediaURL'])

            if 'processed' in (resp.json()[0]['media']['mediaURL']):
                print("Transcription processed!")
                break
        except:
            print("Transcription not processed yet")
            time.sleep(5)


if __name__ == "__main__":
    check_if_transcription_processed(
        'eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjb20uYXVnbWVkaXgiLCJleHAiOjE2NTM1MzExODUsInVpZCI6MjAwMTUsInJscyI6WyJTQ1JJQkUiXX0.Apk3k-5rX7lNkjE7EMMI3XWxKtzbapKqg9C0Q_JDq2Y',
        '22028-1029761-036f86e5-125d-4330-8088-346ae6af2311')
