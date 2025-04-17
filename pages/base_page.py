
import pytest
from utils.request_handler import RequestHandler


class BasePage:
    provider_url = pytest.configs.get_config('provider_base_url')

    def reset_password(self, token=None, headers=None, new_password="newAugPass@#"):
        path_reset_password = f'providers/me/password?newPassword={new_password}'
        if token:
            response = RequestHandler.get_api_response(base_url=self.provider_url, request_path=path_reset_password,
                                                   request_type='POST', token=token)
        elif headers:
            response = RequestHandler.get_api_response(base_url=self.provider_url, request_path=path_reset_password,
                                                       request_type='POST', headers=headers)
        if response.status_code == 200:
            print("Password Changed")

    # def __init__(self, db):
    #     self.db = db
    #
    # def blocked_user(self, user_name):
    #     for _ in range(4):
    #         RequestHandler.get_auth_response(user_name=user_name, password='Augmedix@2311111')
    #
    # def update_user_status(self, key_value, key='doctorEmail', update_key='doctorStatus', update_value='active',
    #                        db_name='dev_augmedix', table_name='doctor'):
    #     query = f"UPDATE {db_name}.{table_name} SET {update_key}='{update_value}' WHERE {key}='{key_value}';"
    #     self.db.execute_query(query)
    #     print(query)
