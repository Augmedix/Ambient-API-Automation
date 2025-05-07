# pylint: disable=no-member
import pytest
from utils.request_handler import RequestHandler
from pages.base_page import BasePage
from utils.api_request_data_handler import APIRequestDataHandler


class CommureTemplatePage(BasePage):
    def __init__(self):
        """
        Initialize the CommureTemplatePage with API request data.
        """
        self.request_data = APIRequestDataHandler("commure_template_api")
        self.base_url = pytest.configs.get_config("commure_template_base_url")

    def commure_template_request(self, method, email, auth_token=None, user_name=None, password=None):
        """
        Generic method to handle GET, POST, PUT, and DELETE requests for Commure templates.
        """
        token = auth_token if auth_token else RequestHandler.get_auth_token(user_name=user_name, password=password)
        headers = self.request_data.get_modified_headers(Authorization=f"Bearer {token}")
        path = f"templates?email={email}"  # Ensure no duplication here

        print(f"Request Path: {path}")
        print(f"Request Headers: {headers}")

        response = RequestHandler.get_api_response(
            base_url=self.base_url,
            request_path=path,
            request_type=method,
            headers=headers,
        )
        return response