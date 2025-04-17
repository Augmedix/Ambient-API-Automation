from utils.testrail.project_handler import ProjectHandler


class TestRunHandler:
    """
    This class deals with creating, displaying, updating or deleting test runs in TestRail.
    """

    def __init__(self, session):
        self.session = session

    def add_testrun_by_project_id(self, project_id, data={}):
        """
        Add a testrun under the specified project.

        Parameters
        ----------
        project_id : number
                     Used for which testrun should be created.
        data    : dictionary
                Used to provide testrun related info like: suite_id, name, description, milestone_id,
                assignedto_id, include_all, case_ids, refs etc.

                keys:
                ----
                suite_id : int (mandatory)
        """
        try:
            self.session.send_post(f'add_run/{project_id}', data)
        except Exception as ex:
            print(f'Error occured during adding testrun!! {str(ex)}')

    def add_testrun_by_project_name(self, project_name, data={}):
        project_id = ProjectHandler(self.session).get_project_id(project_name)
        self.add_testrun_by_project_id(project_id, data)

    def get_all_runs_by_project_id(self, project_id):
        return self.session.send_get(f'get_runs/{project_id}')

    def get_all_runs_by_project_name(self, project_name):
        project_id = ProjectHandler(self.session).get_project_by_name(project_name)['id']
        print(f'Porject ID: {project_id}')
        return self.get_all_runs_by_project_id(project_id)['runs']

    def get_testrun_id(self, project_name, run_name):
        test_runs = self.get_all_runs_by_project_name(project_name)
        for test_run in test_runs:
            extracted_name = test_run['name']
            if extracted_name == run_name:
                return test_run['id']

    def close_testrun_by_id(self, run_id, data={}):
        self.session.send_post(f'close_run/{run_id}', data)

    def close_testrun_by_name(self, project_name, run_name, data={}):
        run_id = self.get_testrun_id(project_name, run_name)
        self.close_testrun_by_id(run_id)

    def close_all_testruns_by_name(self, project_name, run_name):
        test_runs = self.get_all_runs_by_project_name(project_name)

        for test_run in test_runs:
            testrun_name = test_run['name']
            testrun_status = test_run['is_completed']

            if testrun_name == run_name and not testrun_status:
                self.close_testrun_by_id(test_run['id'])

    def delete_testrun_by_id(self, run_id, data={}):
        self.session.send_post(f'delete_run/{run_id}', data)

    def delete_testrun_by_name(self, project_name, run_name, data={}):
        run_id = self.get_testrun_id(project_name, run_name)
        self.delete_testrun_by_id(run_id)

    def delete_all_testruns_by_name(self, project_name, run_name):
        test_runs = self.get_all_runs_by_project_name(project_name)

        for test_run in test_runs:
            testrun_name = test_run['name']
            testrun_status = test_run['is_completed']
            if testrun_name == run_name and not testrun_status:
                self.delete_testrun_by_id(test_run['id'])
