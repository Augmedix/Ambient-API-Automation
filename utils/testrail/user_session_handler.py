import pytest

from utils.testrail.api_client import APIClient
from utils.testrail.credential_manager import CredentialManager


class UserSessionManager:

    def __init__(self, url='https://augmedix.testrail.com'):

        CredentialManager.update_credential()

        self.userid = CredentialManager.get_username()
        self.password = CredentialManager.get_password()
        self.url = url

    def get_session(self):
        client = APIClient(self.url)
        client.user = self.userid
        client.password = self.password

        return client
