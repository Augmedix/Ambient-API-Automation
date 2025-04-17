import pytest
import requests
from requests.structures import CaseInsensitiveDict

from utils.s2t_handler import S2THandler


def log_scribe_out(token):
    log_out_service = pytest.config_parser.get("urls", "log_out_url")
    url = log_out_service
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json, text/plain, */*"
    headers["Accept-Language"] = "en-US,en;q=0.9"
    headers[
        "Authorization"] = f"Bearer {token}"
    headers["Connection"] = "keep-alive"
    headers["Content-Type"] = "application/json"
    # headers["Origin"] = "https://dev2.augmedix.com:8195"
    # headers["Referer"] = "https://dev2.augmedix.com:8195/"
    headers["Sec-Fetch-Dest"] = "empty"
    headers["Sec-Fetch-Mode"] = "cors"
    headers["Sec-Fetch-Site"] = "same-site"
    headers[
        "User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"

    data = '{"logoutType":"inactive"}'

    resp = requests.post(url, headers=headers, data=data)

    print(resp.status_code)


def get_scribe_auth_token_and_logout(username, password):
    token = S2THandler.get_auth_token(username, password)
    log_scribe_out(token)

if __name__ == "__main__":
    token = S2THandler.get_auth_token('shaun_regression_scribe@augmedix.com', 'Reg_1ffff3a11a')
    log_scribe_out(token)