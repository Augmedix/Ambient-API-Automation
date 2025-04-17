import json

import pytest
import requests
from _pytest import config
from requests.structures import CaseInsensitiveDict


def schedule_note_for_scribe(auth, paired_scribe_id):
    api_base_url = pytest.configs.get_config('api_base_url')

    trainer_portal_schedule = pytest.configs.get_config('trainer_portal_schedule')
    print(trainer_portal_schedule)
    url = f"{api_base_url}/{trainer_portal_schedule}"

    headers = CaseInsensitiveDict()
    #headers["authority"] = "stage-api2.augmedix.com"
    headers["accept"] = "*/*"
    headers["accept-language"] = "en-US,en;q=0.9"
    headers[
        "authorization"] = f'Bearer {auth}'
    headers["content-type"] = "application/json"
    #headers["origin"] = "https://staging-trainer-portal.augmedix.com"
    #headers["referer"] = "https://staging-trainer-portal.augmedix.com/"
    headers["sec-ch-ua"] = "Not A;Brand;v=99, Chromium;v=101, Google Chrome;v=101"
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-ch-ua-platform"] = "'Windows"
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-site"
    headers[
        "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"

    var = ''
    if pytest.env is None or pytest.env == 'dev':
        var = '{"videoId":28,"rubricId":45}'

    elif pytest.env == 'stage' or pytest.env == 'staging':
        var = '{"videoId":89,"rubricId":41}'

    elif pytest.env == 'prod' or pytest.env == 'production' or pytest.env == 'live':
        var = '{"videoId":89,"rubricId":41}'



    data = f'{{"title":"test automation","pairedScribeIds":[{paired_scribe_id}],"gracePeriodInSeconds":0,"type":"TAGGED","visits":[{var}]}}'

    print(data)

    resp = requests.post(url, headers=headers, data=data , verify=False)

    print('response is:')
    print(resp.text)
