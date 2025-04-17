import pytest
import requests
from requests.structures import CaseInsensitiveDict


def delete_note_by_id(id, token):
    api_base_url = pytest.configs.get_config('api_base_url')
    note_api = pytest.configs.get_config('notes')
    url = f"{api_base_url}/{note_api}/notes/patient/{id}"

    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json, text/plain, */*"
    headers["accept-language"] = "en-US,en;q=0.9"
    headers[
        "authorization"] = f"Bearer {token}"
    headers["sec-ch-ua"] = "Not A;Brand;v=99, Chromium;v=101, Google Chrome;v=101"
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-ch-ua-platform"] = "Windows"
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-site"
    headers[
        "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"

    resp = requests.delete(url, headers=headers)

    print(resp.text)




