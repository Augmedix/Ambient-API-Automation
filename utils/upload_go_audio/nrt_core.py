import requests
import json
import base64
import datetime
import uuid


def timestamp_millisec64():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def create_start_signal(stream_id, doc_id, note_id, stream_type, media_type):
    start = {
        'name': "start",
        'streamId': stream_id,
        'docId': doc_id,
        'noteId': note_id,
        'type': stream_type,
        'starttime': timestamp_millisec64(),
        'mediatype': media_type
    }

    start_payload = json.dumps(start)
    return start_payload


def create_stop_signal(stream_id, doc_id, note_id, stream_type, media_type):
    stop = {
        'name': "stop",
        'streamId':  stream_id,
        'docId': doc_id,
        'noteId': note_id,
        'type': stream_type,
        'starttime': timestamp_millisec64(),
        'mediatype': media_type,
        'sessionDuration': 50000,
        'lastChunkId': 1,
        'endtime': timestamp_millisec64()
    }

    stop_payload = json.dumps(stop)
    return stop_payload


def create_chunk_signal(file_path, stream_id, stream_type):
    with open(file_path, "rb") as image_file:
        encoded_file = base64.b64encode(image_file.read())

    chunk = {
        'retentionDuration' : 604800000000000,
        'streamId' : stream_id,
        'type' : stream_type,
        'fileName' : "0000001.mp4",
        'sequenceNumber' : 1,
        'initTime' : timestamp_millisec64(),
        'chunkDuration' : 5000000000,
        'file': encoded_file.decode("utf-8")
    }

    chunk_payload = json.dumps(chunk)
    return chunk_payload


def create_completion_signal(stream_id):
    chunk = {
        "streamId": stream_id,
        "sdkName": "upload_tool",
        "sdkVersion": "0.0.0"
    }

    chunk_payload = json.dumps(chunk)
    return chunk_payload


def send_signal(jwt_token, server_url, end_point, payload):
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'Authorization': 'Bearer ' + jwt_token}

    response = requests.post(server_url+end_point, data=payload, headers=headers)
    if response.ok:
        print(end_point + " signal sent", len(payload))
    else:
        print(end_point + " signal sending error:", response)

    return response


def upload_nrt_file(server_url, doc_id, note_id, stream_type, media_type, file_path, jwt_token):
    unique_id = str(uuid.uuid4())
    stream_id = doc_id + '-' + note_id + '-' + unique_id
    print('stream_id', stream_id)

    start_signal = create_start_signal(stream_id, doc_id, note_id, stream_type, media_type)
    resp = send_signal(jwt_token, server_url, '/command', start_signal)
    if not resp.ok:
        return False

    chunk_signal = create_chunk_signal(file_path, stream_id, stream_type)
    resp = send_signal(jwt_token, server_url, '/chunk', chunk_signal)
    if not resp.ok:
        return False

    stop_signal = create_stop_signal(stream_id, doc_id, note_id, stream_type, media_type)
    resp = send_signal(jwt_token, server_url, '/command', stop_signal)
    if not resp.ok:
        return False

    completion_signal = create_completion_signal(stream_id)
    resp = send_signal(jwt_token, server_url, '/streamuploadcompletion', completion_signal)
    if not resp.ok:
        return False

    return True, stream_id
