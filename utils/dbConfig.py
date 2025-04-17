import os
import pymysql
import paramiko
# import pandas as pd
from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
from os.path import expanduser
import pytest
from pathlib import Path
from io import StringIO


ENV = pytest.env

class DB:
    def execute_query(self, sql_query=''):
        if ENV in ('stage', 'staging', 'demo'):
            if ENV in ('stage', 'staging'):
                sql_hostname = pytest.configs.get_config('stage_db_host')
            if ENV in ('demo'):
                sql_hostname = pytest.configs.get_config('demo_db_host')
            sql_username = pytest.configs.get_config('stage_db_username')
            sql_password = pytest.configs.get_config('stage_db_password')
            sql_main_database = pytest.configs.get_config('stage_db_database')
            sql_port = 3306
            ssh_host = pytest.configs.get_config('stage_db_ssh_host')
            ssh_user = pytest.configs.get_config('stage_db_ssh_user')
            ssh_port = 22
            if pytest.enable_jenkins == 'yes':
                self.ssh_pkey = paramiko.RSAKey.from_private_key(StringIO(pytest.configs.get_config('private_key_jenkins')))
            else:
                self.ssh_pkey = paramiko.RSAKey.from_private_key(StringIO(pytest.configs.get_config('private_key_local')))



            with SSHTunnelForwarder(
                    (ssh_host, ssh_port),
                    ssh_username=ssh_user,
                    ssh_pkey=self.ssh_pkey,
                    remote_bind_address=(sql_hostname, sql_port)) as tunnel:

                    conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                            passwd=sql_password, db=sql_main_database,
                            port=tunnel.local_bind_port)

                    cursor = conn.cursor()
                    print('sql_query: ', sql_query)
                    cursor.execute(sql_query)
                    conn.commit()
                    results = cursor.fetchall()
                    print(cursor.fetchone())
                    conn.close()
                    return results
                    
        elif ENV == 'dev':
            dev_cred = {
                'host': pytest.configs.get_config('dev_db_host'),
                'database': pytest.configs.get_config('dev_db_database'),
                'user': pytest.configs.get_config('dev_db_username'),
                'password': pytest.configs.get_config('dev_db_password'),
            }

            conn = pymysql.connect(**dev_cred)

            cursor = conn.cursor()
            print('sql_query: ', sql_query)
            cursor.execute(sql_query)
            conn.commit()
            results = cursor.fetchall()
            print(cursor.fetchone())
            conn.close()
            return results
