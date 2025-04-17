from datetime import datetime

import requests
from pytz import timezone, utc


def get_pst_time():
    date_format='%H:%M'
    date = datetime.now(tz=utc)
    date = date.astimezone(timezone('US/Pacific'))
    pstDateTime=date.strftime(date_format)
    return pstDateTime

def get_pst_date():
    date_format = '%Y-%m-%d'
    date = datetime.now(tz=utc)
    date = date.astimezone(timezone('US/Pacific'))
    pstDateTime = date.strftime(date_format)
    return pstDateTime

def send_create_patient_requset(patient_creation_url, patient_name, pst_time, pst_date, jwt_token):
    headers = {'Authorization': 'Bearer ' + jwt_token}

    url = patient_creation_url + "/providers/me/patients?patientName=" + patient_name + "&startTime=" + pst_time + "&visitDate=" + pst_date
    response = requests.post(url, headers=headers)

    if response.ok:
        print("Patient creation signal sent. Patinet name:", patient_name)
    else:
        print("Patient creation signal sending error:", response)

    return response

def create_patient(patient_creation_url, patient_name, token):
    time = get_pst_time()
    date = get_pst_date()

    resp = send_create_patient_requset(patient_creation_url, patient_name, time, date, token)
    return resp
