class ProjectHandler:

    def __init__(self, session):
        self.session = session

    def get_project_by_id(self, project_id):
        return self.session.send_get(f'get_project/{project_id}')

    def get_project_by_name(self, project_name):
        projects = self.get_all_projects()
        print(projects)

        for project in projects:
            extracted_project_name = project['name']
            if extracted_project_name == project_name:
                return project

    def get_project_id(self, project_name):
        project = self.get_project_by_name(project_name)
        return project['id']

    def get_all_projects(self):
        return self.session.send_get('get_projects')['projects']
