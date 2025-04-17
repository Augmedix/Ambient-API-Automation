from utils.testrail.testrun_handler import TestRunHandler


class TestResultHandler:

    def __init__(self, session):
        self.session = session

    def add_result_for_case(self, run_id, case_id, request_body={}):
        self.session.send_post(
            f'add_result_for_case/{run_id}/{case_id}', request_body)

    def add_result_for_case_by_run_name(self, project_name, run_name, case_id, request_body={}):
        run_id = TestRunHandler(self.session).get_testrun_id(
            project_name, run_name)
        self.add_result_for_case(run_id, case_id, request_body)
