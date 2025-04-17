from io import StringIO

from jproperties import Properties

from utils.app_constants import AppConstant


class ConfigParser:

    def __init__(self):
        self.configs = Properties()
        self.files = []

    def add_file(self, file_name):
        self.files.append(file_name)
        return self

    def load_configs(self):
        for file in self.files:
            try:
                with open(file, 'rb') as config_file:
                    temp_config = Properties()
                    temp_config.load(config_file)

                    for __item in temp_config.items():
                        key = __item[0]
                        value = __item[1].data

                        self.set_config(key, value)
            except FileNotFoundError:
                print(f'Sorry, the file {file} does not exists.')

    def load_config(self, config_path=AppConstant.DEV_CONFIG):
        try:
            with open(config_path, 'rb') as config_file:
                self.configs.load(config_file)
        except FileNotFoundError:
            print(f'Sorry, the file {config_path} does not exists.')

    def get_config(self, key):
        value = self.configs.get(key)
        return None if value is None else value.data.strip()

    def set_config(self, key, value):
        self.configs[key] = value

    def delete_config(self, key):
        del self.configs[key]

    def update_config(self, key, value, config_path=AppConstant.DEV_CONFIG):

        with open(config_path, 'wb') as config_file:
            self.configs[key] = value
            self.configs.store(config_file, encoding="utf-8",
                               strip_meta=False, timestamp=False)


conf = ConfigParser()
conf.add_file(AppConstant.DEV_CONFIG)
conf.load_configs()

count = -1

for i in conf.configs:
    if i.startswith('username'):
        count = count + 1

print(count)
