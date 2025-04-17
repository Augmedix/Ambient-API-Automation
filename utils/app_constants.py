from os.path import dirname, join


class AppConstant:

    PROJECT_ROOT = dirname(dirname(__file__))
    RESOURCE_FOLDER = join(PROJECT_ROOT, 'resources')
    TESTRAIL_CONFIG = join(RESOURCE_FOLDER, 'testrail.properties')
    SYSTEM_CONFIG = join(RESOURCE_FOLDER, 'system.properties')
    DEV_CONFIG = join(RESOURCE_FOLDER, 'dev.properties')
    DEMO_CONFIG = join(RESOURCE_FOLDER, 'demo.properties')
    STAGING_CONFIG = join(RESOURCE_FOLDER, 'staging.properties')
    PRODUCTION_CONFIG = join(RESOURCE_FOLDER, 'production.properties')
    DATA_CONFIG = join(RESOURCE_FOLDER, 'data.properties')
    REQUEST_DATA_FOLDER = join(RESOURCE_FOLDER, 'request_data')
    SKIPPED_TESTCASES_FILE = join(RESOURCE_FOLDER, 'skipped_testcases.properties')

