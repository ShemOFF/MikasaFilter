class Base:
    from project_config import UNIX_CHECK_DATETIME
    import datetime
    import json
    import requests
    from urllib import parse
    import time

    REQUEST_REPEAT = 5

    def __init__(self, url_org_repo: str, date_pattern: str):
        self.url_org_repo = url_org_repo
        self.date_pattern = date_pattern

    def __del__(self):
        self.url_org_repo = None
        del self.url_org_repo

        self.date_pattern = None
        del self.date_pattern

    def add_url_org_and_path(self, *paths: str) -> str:
        result_url = self.parse.urljoin(self.url_org_repo, '/'.join(paths))
        return result_url

    def add_url_and_path(self, url: str, *paths: str) -> str:
        result_url = self.parse.urljoin(url, '/'.join(paths))
        return result_url

    def check_date_release(self, date_release: str) -> bool:
        try:
            version_date_release = self.datetime.datetime.strptime(date_release, self.date_pattern)
            unix_time_date_release = self.datetime.datetime.timestamp(version_date_release)

            if unix_time_date_release >= self.UNIX_CHECK_DATETIME:
                return False
            return True
        except (ValueError, Exception):
            return False

    def get_repo_text(self, url: str) -> str:
        try:
            request_npm = self.requests.get(url)
            if not request_npm.ok:
                return 'error'
            return request_npm.text
        except (ValueError, Exception):
            return 'error'

    def post_repo_text(self, url: str, data: bytes) -> str:
        try:
            request_npm = self.requests.post(url, data=data)
            if not request_npm.ok:
                return 'error'
            return request_npm.text
        except (ValueError, Exception):
            return 'error'

    def check_response_result(self, type_request: str = 'get_text', **request_param) -> str:
        request_types: dict = {'get_text': self.get_repo_text,
                               'post_text': self.post_repo_text}
        if type_request not in request_types:
            return 'error'
        if type_request == 'get_text' and \
                'url' not in request_param and \
                len(request_param) != 1:
            return 'error'
        if type_request == 'post_text' and \
                'url' not in request_param and 'data' not in request_param and \
                len(request_param) != 2:
            return 'error'
        for request_number in range(self.REQUEST_REPEAT):
            request: str = request_types[type_request](**request_param)
            if request:
                return request
            else:
                self.time.sleep(1)
        return 'error'

    def get_repo_json(self, url: str) -> dict:
        try:
            request = self.check_response_result(type_request='get_text', url=url)
            request_json = self.json.loads(request)
            return request_json.copy()
        except (ValueError, Exception):
            return {"error": "Not found"}

    def post_repo_json(self, url: str, data: bytes) -> dict:
        try:
            request = self.check_response_result(type_request='post_text', url=url, data=data)
            if request == 'error':
                return {"error": "Not found"}
            request_json = self.json.loads(request)
            return request_json.copy()
        except (ValueError, Exception):
            return {"error": "Not found"}


class NPM(Base):

    def __init__(self, url_org_repo: str, date_pattern: str):
        super().__init__(url_org_repo, date_pattern)
        self.json_package: dict = {}

    def __del__(self):
        super().__del__()
        self.json_package = None
        del self.json_package

    def __check_valid_time(self, version: str, date_release: str) -> dict:
        max_version = ''
        if self.check_date_release(date_release=date_release):
            if 'created' == version or 'modified' == version:
                return {'status': True, 'version': ''}
            pre_version = version.split('.')
            if len(pre_version) != 3:
                return {'status': True, 'version': ''}
            else:
                major_version, minor_version, micro_version = pre_version
            if major_version.isdigit() and minor_version.isdigit() and micro_version.isdigit():
                max_version = version
            return {'status': True, 'version': max_version}

        else:
            return {'status': False, 'version': ''}

    def __del_bad_version_package(self, version: str):
        # if 'time' in self.json_package:
        self.json_package['time'].pop(version, None)
        if 'versions' in self.json_package:
            self.json_package['versions'].pop(version, None)

    def __finally_edit_package_json(self, max_version: str):
        self.json_package['dist-tags'] = {'latest': max_version}
        self.json_package['_rev'] = '1-0'

        if self.json_package['time']:
            end_time_element: str = list(self.json_package['time'].keys())[-1]
            self.json_package['time']['modified'] = self.json_package['time'][end_time_element]

    def get_repo_corrected_json(self, package_name: str) -> dict:
        url = self.add_url_org_and_path(package_name)
        self.json_package = self.get_repo_json(url)

        if 'error' in self.json_package:
            return {"error": "Not found"}
        max_version: str = '0.0.0'
        json_time = self.json_package['time'].copy()
        for version in json_time:
            date_release = json_time[version]
            result_check_valid_time = self.__check_valid_time(version, date_release)
            if not result_check_valid_time['status']:
                self.__del_bad_version_package(version)
                continue
            if not result_check_valid_time['version']:
                continue
            elif result_check_valid_time['version']:
                max_version = version
        self.__finally_edit_package_json(max_version)
        return self.json_package.copy()

    def check_valid_tgz(self, package: str, tgz_name: str) -> bool:
        version_smash = package.split('/')[-1] + "-"
        version = tgz_name.split(version_smash)[-1]
        url_check = self.add_url_org_and_path(package)
        json_repo = self.get_repo_json(url_check)
        if 'time' not in json_repo:
            return False
        time_version = json_repo['time']
        if self.check_date_release(time_version[version]):
            return True
        else:
            return False


class Pipe(Base):

    def get_repo_pypi_json(self, package_name: str) -> dict:
        url = self.add_url_org_and_path('pypi', package_name, 'json')
        json_package = self.get_repo_json(url)
        return json_package

    def __check_platform_package_from_version(self, platform_version: dict) -> dict:
        valid_package: dict = {}
        for platform_version in platform_version:
            date_release = platform_version['upload_time_iso_8601']
            if not self.check_date_release(date_release=date_release):
                continue
            filename = platform_version['filename']
            url = platform_version['url']
            if url[:8] != r'https://':
                url = r'https://' + platform_version['url']
            valid_package[filename] = url
        return valid_package

    def get_repo_corrected_json(self, package_name: str) -> dict:
        valid_package: dict = {}
        json_package = self.get_repo_pypi_json(package_name)
        if 'error' in json_package:
            return {}
        version_release = json_package['releases']
        for full_version in version_release:
            platform_version = version_release[full_version]
            valid_package.update(self.__check_platform_package_from_version(platform_version))
        return valid_package
