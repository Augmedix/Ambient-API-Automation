import os
import platform

import cryptocode


class CredentialManager:

    @staticmethod
    def get_username():
        """
        Retrieve the username/email set earlier by a user.
        """
        return os.getenv('testrail_username')

    @staticmethod
    def get_password():
        """
        Retrieve the decrypted password set earlier by a user.
        """
        password = os.getenv('testrail_password')
        return cryptocode.decrypt(password, 'h@rD2R340p@55w@rd')

    @staticmethod
    def set_env(environment_variable_name, value):
        if platform.system() == 'Windows':
            from py_setenv import set_variable
            set_variable(environment_variable_name, value, user=True)
        else:
            with open(os.path.expanduser('~/.bashrc'), 'a') as bashrc_file:
                bashrc_file.write(f'\nexport {environment_variable_name}={value}\n')

    @staticmethod
    def update_credential():
        """
        Set user's credentials if it is not already set. Accept space separated username/email and password.
        """
        if not CredentialManager.is_credentials_set():
            username, password = input('\nNo valid credentials found for TestRail. Please input space separated username/email & password.\n').split()

            os.environ['testrail_username'] = username
            os.environ['testrail_password'] = password
            CredentialManager.set_env('testrail_username', username)
            CredentialManager.set_env('testrail_password', cryptocode.encrypt(password, 'h@rD2R340p@55w@rd'))

    @staticmethod
    def is_credentials_set():
        """
        Check if the user's credentials are set in the environment.
        """
        username = os.getenv('testrail_username')
        password = os.getenv('testrail_password')

        return username and password
