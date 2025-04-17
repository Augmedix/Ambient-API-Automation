from utils.upload_go_audio.nrt_core import upload_nrt_file
from utils.upload_go_audio.authentication import get_auth_token
import pytest
import jwt


def upload_audio_to_go_note(note_id, file_path, username=None, password=None, auth_token=None):
    doc_id = None

    if auth_token:
        token = auth_token
    else:
        token = get_auth_token(username, password)
    if not token:
        print("Terminating: auth token retrival issue.")
        return
    decoded = jwt.decode(token, options={"verify_signature": False})

    if decoded.get("guid") is not None:
        doc_id = decoded.get("guid")
        print("Lynx Provider")

    success, stream_id = upload_nrt_file(pytest.configs.get_config('file_upload_server_url'), str(doc_id), note_id, 'visit',
                              'audio', file_path, token)

    if success:
        print("Uploaded successfully")
    else:
        print("There was an issue. Uploading failed")

    return stream_id
    
    
