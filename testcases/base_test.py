import pytest

from resources.data import Data
from utils.dbConfig import DB
from utils.request_handler import RequestHandler


class BaseTest:
    provider_url = pytest.configs.get_config('provider_base_url')
    user_name = ''
    password_hash = ''


    @pytest.fixture
    def setup_testcase_for_user_active_testcases(self):
        self.db = DB()
        self.data = Data()
        yield
        query_updated = self.data.update_dr_status_query.replace(self.data.doctorEmailPlaceholder, self.user_name).replace(
                                                                            self.data.doctorStatusPlaceholder, 'active')
        print(f'Query: {query_updated}')
        self.db.execute_query(query_updated)

    @pytest.fixture
    def setup_for_password_reset_testcases(self):
        self.db = DB()
        self.data = Data()
        yield
        password_reset_query = self.data.update_dr_password_query.replace(self.data.doctorEmailPlaceholder, self.user_name).replace(
                                                                                    self.data.doctorPasswordHashPlaceholder, self.password_hash)
        self.db.execute_query(password_reset_query)
