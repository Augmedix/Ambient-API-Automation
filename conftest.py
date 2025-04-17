import sys
import os
import pytest
from jproperties import Properties

from utils.app_constants import AppConstant
from utils.config_parser import ConfigParser
from cryptography.fernet import Fernet


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    env = config.getoption('--env')
    url = config.getoption('--url')
    marker = config.getoption('-m')

    configs = ConfigParser()

    if env is None or env == 'dev':
        configs.add_file(AppConstant.DEV_CONFIG)
        pytest.conf = AppConstant.DEV_CONFIG
        pytest.env = env
    elif env == 'demo':
        configs.add_file(AppConstant.DEMO_CONFIG)
        pytest.conf = AppConstant.DEMO_CONFIG
        pytest.env = env
    elif env == 'stage' or env == 'staging':
        configs.add_file(AppConstant.STAGING_CONFIG)
        pytest.conf = AppConstant.STAGING_CONFIG
        pytest.env = env
    elif env == 'prod' or env == 'production' or env == 'live':
        configs.add_file(AppConstant.PRODUCTION_CONFIG)
        pytest.conf = AppConstant.PRODUCTION_CONFIG
        pytest.env = env
    else:
        sys.exit(
            f'Invalid option. Please provide either of the following values: dev, staging, production...')

    configs.add_file(AppConstant.SYSTEM_CONFIG)
    configs.add_file(AppConstant.TESTRAIL_CONFIG)
    configs.add_file(AppConstant.DATA_CONFIG)
    pytest.conf_data = AppConstant.DATA_CONFIG
    pytest.marker = marker

    configs.load_configs()

    if url is not None:
        configs.set_config('url', url)

    #   Load & set environment variables
    env_var_prefix = configs.get_config('environment_variable_prefix')

    env_vars = os.environ
    secret_key = os.environ.get('SECRET_KEY')
    cipher = Fernet(secret_key)
    for key, value in env_vars.items():
        if key.startswith(env_var_prefix):
            truncated_key = key.replace(env_var_prefix, '').lower()
            decrypted_value = cipher.decrypt(str.encode(value)).decode()
            configs.set_config(truncated_key, decrypted_value)

    pytest.configs = configs
    pytest.url = configs.get_config('url')
    pytest.report_title = config.getoption('--report-title')
    pytest.run_skips = config.getoption('--run-skips')
    pytest.enable_jenkins = config.getoption('--enable-jenkins')


def pytest_collection_modifyitems(items):
    """
    Modifies the collected test cases by adding skip marker. Test case lists are read from
    'skipped_testcases.properties' file under 'resources' folder. Test cases are listed as key
    & associated comments are placed as the value of that particular test case.
    """
    with open(AppConstant.SKIPPED_TESTCASES_FILE, 'rb') as config_file:
        temp_config = Properties()
        temp_config.load(config_file)
        skipped_tcs = {}
        for __item in temp_config.items():
            key = __item[0]
            value = __item[1].data
            skipped_tcs[key] = value

    for item in items:
        if item.name in skipped_tcs:
            skip_info_list = skipped_tcs[item.name].split('|')

            if len(skip_info_list) == 1:
                item.add_marker(pytest.mark.skip(reason=skip_info_list[0]))
            else:
                item.add_marker(pytest.mark.skipif(pytest.env == skip_info_list[0], reason=skip_info_list[1]))

@pytest.fixture(autouse=True)
def setup_testcase(request):
    request.cls.tc_name = request.node.name
    request.cls.suite_name = request.cls.__name__


def pytest_addoption(parser):
    parser.addoption('--env', action='store', default='dev',
                     help='env: dev, demo, staging or prod/live')
    parser.addoption('--url', action='store', help='url: dev, demo, staging or production url. If it is provided,'
                                                   'this value will override the value provided by config file.')
    parser.addoption('--repeat', action='store', type=int,
                     default=1, help='Run eah test specified number of times.')
    parser.addoption('--report-title', action='store', default='Lynx API Automation Report')
    parser.addoption('--run-skips', action='store', default='no', help='Enable skipped test cases.')
    parser.addoption('--enable-jenkins', action='store', default='no', help='Enable running from local machine/Jenkins.'
                                                                            '--enable-jenkins=no by default.')
