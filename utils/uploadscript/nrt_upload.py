import argparse
import json
import sys

import jwt

from .authentication import get_auth_token
from .nrt_core import upload_nrt_file
from .patient_creation import create_patient


def nrt_api(serverurl,streamingtype,mediatype,filepath,emailid,password,authurl,patient_creation_url,patient_name):
    '''
                parser = argparse.ArgumentParser()
                parser.add_argument("-url", "--serverurl", dest="serverurl", help="NRT Server URL. i.e. https://mcu-test1.augmedix.com:30010", required=True)
                parser.add_argument("-stype", "--streamingtype", dest="streamingtype", help="streaming type. i.e. recording/visit/dictation", required=True)
                parser.add_argument("-mtype", "--mediatype", dest="mediatype", help="media type. i.e. audio/video", required=True)
                parser.add_argument("-file", "--filepath", dest="filepath", help="file path of local media.", required=True)
                parser.add_argument("-email", "--emailid", dest="emailID", help="NRT provider's email ID.", required=True)
                parser.add_argument("-pass", "--password", dest="password", help="NRT provider's password.", required=True)
                parser.add_argument("-auth", "--authurl", dest="authURL", help="URL for retrieving auth token", required=True)
                parser.add_argument("-patient", "--patient_creation_url", dest="patient_creation_url", help="URL for patient creation", required=True)
                parser.add_argument("-name", "--patient_name", dest="patient_name", help="Patient name", required=True)
                args = parser.parse_args()
                '''
    token = get_auth_token(authurl, emailid, password)
    print(token)
    if token == "":
        print("Terminating: auth token retrival issue.")
        return

    decoded = jwt.decode(token, options={"verify_signature": False})
    docid = decoded["uid"]

    noteid = 0
    visit_start_time = ''
    response = create_patient(patient_creation_url, patient_name, token)
    if response.ok == False:
        return
    else:
        print("Patient created successfully :", response.text)
        patient_info_parse = json.loads(response.text)
        noteid = patient_info_parse["noteId"]
        visit_start_time = patient_info_parse["visitStartTime"]
        if noteid == 0:
            print("Terminating: invalid noteID.")
            return

    success = upload_nrt_file(serverurl,
                              str(docid),
                              str(noteid),
                              streamingtype,
                              mediatype,
                              filepath,
                              token)
    print(success)
    if success[0]:
        print("Uploaded successfully")
    else:
        print("There was an issue. Uploading failed")

    return success, visit_start_time



