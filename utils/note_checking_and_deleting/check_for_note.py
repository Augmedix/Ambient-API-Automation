import datetime
import json
from datetime import datetime

import pytest
import pytz
import requests
from requests.structures import CaseInsensitiveDict

import utils.note_checking_and_deleting.delete_note as delete_note
from utils.note_checking_and_deleting.get_auth_token import get_auth_token


def check_current_notes_and_delete():
    api_base_url = pytest.configs.get_config('api_base_url')
    note_api = pytest.configs.get_config('notes')
    token = get_auth_token('s2tnrtscribe@augmedix.com', '@ugmed1X@')
    print(token)
    pst = pytz.timezone('America/Los_Angeles')
    date = datetime.now(pst)

    date_time = date.strftime("%d-%m-%Y")
    print("date and time:", date_time)

    url = f"{api_base_url}/{note_api}/notes/patients?patientVisitDate={date_time}&providerId={pytest.configs.get_config('provider_id')}&scribeControl=Full%20Control&trainerNote=false&providerEmail=s2tnrtprovider@augmedix.com&providerFirstName=S2T&providerLastName=NRT&siteId={pytest.configs.get_config('site_id')}&nonRealTimeMode=true"
    print(url)
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

    resp = requests.get(url, headers=headers)

    print(len(resp.json()))
    print(resp.text)
    for x in resp.json():
        #print(json.dumps(x, indent=4, sort_keys=True))
        print(x['id'])
        delete_note.delete_note_by_id(x['id'], token)

    return token
if __name__=="__main__":
    check_current_notes_and_delete()