import time
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import datetime
import string
import random
import pytz
from utils.request_handler import RequestHandler
import jwt



def wait_for_next_minute():
    # Check the current second is between 40 to 59 seconds. If it is then waiting 20 seconds.
    myobj = datetime.datetime.now()
    print(myobj.second)
    if 40 <= myobj.second <= 59:
        print('waiting 20 seconds')
        time.sleep(20)


def generate_random_alphanumeric_string(string_lenght=10):
    """
    Generates random alphanumeric string for specified length.
    :param string_lenght: length of the expected random string. Default length is 10.
    :return: alphanumeric string of specified length.
    """
    alpha_numeric_string = string.ascii_letters + string.digits
    return ''.join(random.choice(alpha_numeric_string) for _ in range(string_lenght))


def is_subset(json_object_1, json_object_2):
    for key, value in json_object_1.items():
        if key not in json_object_2:
            return False
        if value != json_object_2.get(key, None):
            return False
    return True


def get_formatted_date_str(_days=0, _date_format="%Y-%m-%dT%H:%M:%S"):
    date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=_days)
    return date.strftime(_date_format)


def get_iso_formatted_datetime_str(_days=0):
    # ISO DateTime Format yyyy-MM-dd'T'HH:mm:ss.SSSZ, e.g. "2000-10-31T01:30:00.000-05:00".
    date = datetime.datetime.now() + datetime.timedelta(days=_days)
    date = date.astimezone(datetime.timezone.utc)
    date = date.isoformat(timespec='milliseconds')
    return date.replace('+00:00', 'Z')

def get_current_pst_time():
    # Set the time zone to PST
    tz = pytz.timezone('US/Pacific')
    # Get the current time in PST
    current_time = datetime.datetime.now(tz)
    # Format the time in the 12-hour clock format with AM/PM
    formatted_time = current_time.strftime("%I:%M %p")
    return formatted_time


def compare_date_str(actual_date_str, expected_date_str, _formate="%Y-%m-%dT%H:%M:%S"):
    # "2022-12-30T08:50:35.000+00:00"
    # "2022-12-30T08:50:35Z"
    # "2022-12-30T08:50:35.35435Z"
    actual_date_str = datetime.datetime.strptime(actual_date_str[:19], _formate)
    expected_date_str = datetime.datetime.strptime(expected_date_str[:19], _formate)
    return actual_date_str == expected_date_str


def get_current_pst_time_and_date():
    pst = pytz.timezone('US/Pacific')
    now_pst = datetime.datetime.now(pst)
    return now_pst.strftime('%H:%M:%S'), now_pst.strftime('%Y-%m-%d'), now_pst


def validate_response_schema(response_json, schema_path):
    """
    Validate the response JSON against the provided JSON schema.
    :param response_json: The JSON response to validate.
    :param schema_path: Path to the JSON schema file.
    """
    try:
        # Load the schema from the file
        with open(schema_path, "r") as schema_file:
            schema = json.load(schema_file)

        # Log the schema and response for debugging
        print(f"Schema loaded from {schema_path}: {json.dumps(schema, indent=4)}")
        print(f"Response JSON to validate: {json.dumps(response_json, indent=4)}")

        # Validate the response JSON against the schema
        validate(instance=response_json, schema=schema)
        print("Response JSON is valid against the schema.")

    except ValidationError as e:
        # Log the validation error and raise an assertion        # Log the validation error and raise an assertion
        print(f"Validation Error: {e.message}")
        print(f"Validation Error: {e.message}")


