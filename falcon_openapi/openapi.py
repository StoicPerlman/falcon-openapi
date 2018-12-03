import json
from inspect import stack
from os.path import abspath, dirname
from pathlib import Path
from urllib.parse import urlparse

import yaml

OPENAPI_FILE_ERROR = 'Unable to find openapi-spec.yml or openapi-spec.yaml\n' \
                        + 'Checking for file in {}'


class OpenApi():
    """
    Loads openapi-spec for falcon apps. Must be instantiated from an onject
    that was instantiated inside falcon's main app file 
    """

    def __init__(self, file_path=None, raw_json=None, raw_yaml=None, raw_dict=None):

        self.app_dir = self.get_app()

        if not file_path and not raw_json and not raw_yaml and not raw_dict:
            file_path = self.app_dir + 'openapi-spec.yml'
            self.file_path = file_path

            if not Path(file_path).exists():
                file_path = self.app_dir + 'openapi-spec.yaml'
                self.file_path = file_path

                if not Path(file_path).exists():
                    raise FileNotFoundError(OPENAPI_FILE_ERROR.format(self.app_dir))

        if raw_json:
            self.spec = json.loads(raw_json)
        elif raw_yaml:
            self.spec = yaml.safe_load(raw_yaml)
        elif file_path:
            self.file_path = file_path
            with open(file_path) as f:
                if file_path.endswith('json'):
                    self.spec = json.load(f)
                elif file_path.endswith('yml') or file_path.endswith('yaml'):
                    self.spec = yaml.safe_load(f)
        elif raw_dict:
            self.spec = raw_dict

        self.base_path = ''

        if 'servers' in self.spec and isinstance(self.spec['servers'], list):
            servers = self.spec['servers']

            for server in servers:
                if 'url' in server:
                    url = urlparse(server['url'])
                    self.base_path = url.path
        elif 'basePath' in self.spec and isinstance(self.spec['basePath'], str):
            self.base_path = self.spec['basePath']

    def get_app(self):
        """Finds falcon's main app directory"""
        caller_file = abspath((stack()[3])[1])
        caller_dir = dirname(caller_file) + '/'
        return caller_dir
