"""
Provide DB Manager to execute queries on selected DB. Moreover, start/stop tunnelling is also provided
to bypass VPN.
"""
# pylint: skip-file
from io import StringIO

import paramiko
import pymysql
import pytest
from sshtunnel import SSHTunnelForwarder


# pylint: disable=too-many-instance-attributes
class DBManager:
    """
    Handles task related creating db connection, destroying connection, execute query etc.
    """

    def __init__(self, db_name='dev_augmedix') -> None:
        env = pytest.env
        self.db_host = pytest.configs.get_config(f'db_host_{env}')
        self.db_user = pytest.configs.get_config(f'db_user_{env}')
        self.db_password = pytest.configs.get_config(f'db_password_{env}')
        self.db_name = db_name

        self.ssh_host = pytest.configs.get_config('ssh_host')
        self.ssh_port = 22
        self.ssh_user = pytest.configs.get_config('ssh_user')

        if pytest.enable_jenkins == 'yes':
            self.ssh_pkey = paramiko.RSAKey.from_private_key(
                StringIO(pytest.configs.get_config('private_key_jenkins')))
        else:
            self.ssh_pkey = paramiko.RSAKey.from_private_key(
                StringIO(pytest.configs.get_config('private_key_local')))

        self.server = None

    def get_db_connection(self, db_name=None):
        if db_name is None:
            db_name = pytest.configs.get_config('db_name')
        if pytest.env == 'dev':
            db_connection = pymysql.connect(
                host=self.db_host,
                user=self.db_user,
                passwd=self.db_password,
                db=db_name,
                port=3306,
                cursorclass=pymysql.cursors.DictCursor)
            return db_connection
        if pytest.env in ('stage', 'staging'):
            db_connection = pymysql.connect(
                host='127.0.0.1',
                user=self.db_user,
                passwd=self.db_password,
                db=db_name,
                port=self.server.local_bind_port,
                cursorclass=pymysql.cursors.DictCursor)
            return db_connection

        print('Live DB connection is not supported.')
        return None

    def start_tunnel(self):
        if pytest.env in ('stage', 'staging'):
            server = SSHTunnelForwarder(
                self.ssh_host,
                ssh_username=self.ssh_user,
                ssh_pkey=self.ssh_pkey,
                remote_bind_address=(self.db_host, 3306),
                local_bind_address=('localhost', 33006)
            )

            self.server = server
            self.server.start()
            print(f'Tunnelling started at {server.local_bind_port}.')
        elif pytest.env in ('prod', 'live'):
            print('Live db connection is not supported yet.')

    def stop_tunnel(self):
        if self.server:
            self.server.stop()
            print('Tunnelling stopped...')

    def get_row(self, db_cursor, sql_query):
        db_cursor.execute(sql_query)
        return db_cursor.fetchone()

    def get_rows(self, db_cursor, query_string):
        return db_cursor.execute(query_string).fetchall()

    def execute_query(self, query_string, fetch_one=True, commit=False):
        """
        Execute a query and perform commit if necessary.
        :param query_string - query to executed
        :param fetch_one - fetch only single row by default.
        :param commit - whether to commit the executed query
        """
        db_connection = self.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(query_string)
        if commit:
            db_connection.commit()
            return None
        if fetch_one:
            return db_cursor.fetchone()
        return db_cursor.fetchall()


class TestDB:
    """
    Dummy test case for DB handling.
    """
    def test_db_connection(self):
        db_manager = DBManager()
        db_manager.start_tunnel()
        result = db_manager.execute_query(
            query_string='SELECT scribePasswordOld FROM scribe WHERE scribeEmail = "test_reset_scribe@augmedix.com";')

        db_manager.stop_tunnel()

        print(f'Result: {result}, {result["scribePasswordOld"]}')
