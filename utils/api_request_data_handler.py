import json
import os

from utils.app_constants import AppConstant

class APIRequestDataHandler:
    """
    This class is mainly responsible for loading request data from saved json files. To get the data
    loaded user must initialize the class with the expected json data file's name (excluding extension).
    All the json data files assume to be in the "request_data" folder under "resources" folder.
    """

    def __init__(self, datatype='') -> None:
        with open(os.path.join(AppConstant.REQUEST_DATA_FOLDER, f'{datatype}.json'), 'r', encoding='UTF-8') as json_file:
            request_data = json.loads(json_file.read())

        self.request_data = request_data
        self.datatype = datatype

    def get_payload(self, name='payload'):
        """
        Returns the payload as json object.

        Returns:
            json_object: which represents the payload for the request to be sent.
        """
        return self.request_data[name]

    def get_headers(self):
        """
        Returns the headers as json object.
        Returns:
            json_object: which represents the headers for the request to be sent.
        """
        return self.request_data['headers']

    def get_params(self):
        """
        Returns the params as json object.
        Returns:
            json_object: which represents the params for the request to be sent.
        """
        return self.request_data['params']

    def get_modified_payload(self, name='payload', **kwargs):
        """
        Returns the payload as json object after modifying the attributes according to kwargs.
        If the passed keyword argument is not present in the existing payload then it'll be added
        to the existing payload. Otherwise, existing attributes will be modified/updated by the
        keyworad argument value.

        If the payload is a list then user need to provide index to modify the specific object in
        the list. Otherwise, it will modify all the objects in the payload list with the provided.

        Returns:

            json_object: which represents the payload for the request to be sent.
        """
        payload = self.get_payload(name)

        if isinstance(payload, list):
            if 'index' in kwargs:
                index = kwargs['index']
                del kwargs['index']
                expected_object = payload[index]
                payload[index] = self.update_json(expected_object, **kwargs)
                print(f'Expected After: {payload}')
            else:
                for index, _ in enumerate(payload):
                    self.update_json(payload[index], **kwargs)
        else:
            self.update_json(payload, **kwargs)

        return payload

    def get_modified_headers(self, **kwargs):
        """
        Returns the headers as json object after modifying the attributes according to kwargs.
        If the passed keyword argument is not present in the existing headers then it'll be added
        to the existing headers. Otherwise, existing attributes will be modified/updated by the
        keyworad argument value.
        Returns:
            json_object: which represents the headers for the request to be sent.
        """
        headers = self.get_headers()
        for key, value in kwargs.items():
            headers[key] = value

        return headers

    def get_modified_params(self, **kwargs):
        """
        Returns the params as json object after modifying the attributes according to kwargs.
        If the passed keyword argument is not present in the existing params then it'll be added
        to the existing params. Otherwise, existing attributes will be modified/updated by the
        keyworad argument value.
        Returns:
            json_object: which represents the params for the request to be sent.
        """
        params = self.get_params()
        for key, value in kwargs.items():
            params[key] = value

        return params

    def update_json(self, joson_object, **kwargs):
        """
        Update json object.

        Args:
            joson_object (json): JSON object which needs to modify/update.
            kwargs: keyword arguments for adding/updating attributes of the joson_object.

        Returns:
            JSONObject: modified json_object.
        """
        kwargs.pop('index', None)   # Remove the index key.

        for key, value in kwargs.items():
            joson_object[key] = value

        return joson_object
