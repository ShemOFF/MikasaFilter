class Base:
    from project_config import DEFAULT_DATE_PATTERN, DEFAULT_MORATORIUM_DATE
    import datetime
    from dateutil.relativedelta import relativedelta
    import json
    import requests
    from urllib import parse
    import time
    from abc import abstractmethod

    REQUEST_REPEAT = 5

    def __conversion_moratorium_date_from_shift(self, custom_moratorium_date: str):
        try:
            month: int = 0
            date_split: list = custom_moratorium_date.split('-')

            if len(date_split) == 1 and date_split[0].isdigit():
                day = int(date_split[0])
            elif len(date_split) == 2 and date_split[0].isdigit() and date_split[1].isdigit():
                day = int(date_split[0])
                month = int(date_split[1])
            else:
                self.moratorium_date = 'Error: incorrect date'
                return

            if day > 31 or day < 0:
                self.moratorium_date = 'Error: incorrect day (range {0-31})'
                return
            if month > 96 or month < 0:
                self.moratorium_date = 'Error: incorrect month (range{0-96})'
                return

            date_difference = self.datetime.date.today() + self.relativedelta(months=-month, days=-day)
            self.moratorium_date = date_difference.strftime(self.DEFAULT_DATE_PATTERN)

        except Exception:
            self.moratorium_date = 'Error: Exception'

    def __init__(self, url_org_repo: str,
                 package_date_pattern: str = None,
                 custom_moratorium_date: str = None,
                 package_name: str = None):

        self.url_org_repo = url_org_repo
        self.package_date_pattern = package_date_pattern
        if custom_moratorium_date:
            self.__conversion_moratorium_date_from_shift(custom_moratorium_date)
        else:
            self.moratorium_date = self.DEFAULT_MORATORIUM_DATE
        self.package_name = package_name

    def __del__(self):
        self.url_org_repo = None
        del self.url_org_repo

        self.package_date_pattern = None
        del self.package_date_pattern

        self.custom_moratorium_date = None
        del self.custom_moratorium_date

        self.moratorium_date = None
        del self.moratorium_date

        self.package_name = None
        del self.package_name

    def add_url_org_and_path(self, *paths: str) -> str:
        result_url = self.parse.urljoin(self.url_org_repo, '/'.join(paths))
        return result_url

    def add_url_and_path(self, url: str, *paths: str) -> str:
        result_url = self.parse.urljoin(url, '/'.join(paths))
        return result_url

    def check_date_release(self, date_release: str) -> bool:
        try:
            if not self.package_date_pattern or not self.moratorium_date:
                return False

            check_moratorium_date = self.datetime.datetime.strptime(self.moratorium_date,
                                                                    self.DEFAULT_DATE_PATTERN)
            unix_time_moratorium_date = self.datetime.datetime.timestamp(check_moratorium_date)

            version_date_release = self.datetime.datetime.strptime(date_release,
                                                                   self.package_date_pattern)
            unix_time_date_release = self.datetime.datetime.timestamp(version_date_release)

            if unix_time_date_release >= unix_time_moratorium_date:
                return False
            return True
        except (ValueError, Exception):
            return False

    def get_repo_text(self, url: str) -> str:
        try:
            request_npm = self.requests.get(url)
            request_npm.close()
            if not request_npm.ok:
                return 'error'
            return request_npm.text
        except (ValueError, Exception):
            return 'error'

    def post_repo_text(self, url: str, data: bytes) -> str:
        try:
            request_npm = self.requests.post(url, data=data)
            request_npm.close()
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

    @abstractmethod
    def get_repo_corrected_json(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_date_upload_package(self, *args, **kwargs):
        pass


class NPM(Base):

    def get_repo_npm_json(self):
        if self.package_name:
            url = self.add_url_org_and_path(self.package_name)
            self.json_package = self.get_repo_json(url)
        else:
            self.json_package = {"error": "Not self.package_name object"}

    def __init__(self, url_org_repo: str,
                 package_date_pattern: str = None,
                 custom_moratorium_date: str = None,
                 package_name: str = None):
        super().__init__(url_org_repo, package_date_pattern, custom_moratorium_date, package_name)
        self.json_package: dict = {}
        self.get_repo_npm_json()

    def __del__(self):
        super().__del__()
        self.json_package = None
        del self.json_package

    def __get_valid_time(self, version: str, date_release: str) -> dict:
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
        self.json_package['time'].pop(version, None)
        if 'versions' in self.json_package:
            self.json_package['versions'].pop(version, None)

    def __finally_edit_package_json(self, max_version: str):
        self.json_package['dist-tags'] = {'latest': max_version}
        self.json_package['_rev'] = '1-0'

        if self.json_package['time']:
            end_time_element: str = list(self.json_package['time'].keys())[-1]
            self.json_package['time']['modified'] = self.json_package['time'][end_time_element]

    def get_repo_corrected_json(self) -> dict:
        if 'error' in self.json_package:
            return {"error": "Not found"}
        max_version: str = '0.0.0'
        json_time = self.json_package['time'].copy()
        for version in json_time:
            date_release = json_time[version]
            result_check_valid_time = self.__get_valid_time(version, date_release)
            if not result_check_valid_time['status']:
                self.__del_bad_version_package(version)
                continue
            if not result_check_valid_time['version']:
                continue
            elif result_check_valid_time['version']:
                max_version = version
        self.__finally_edit_package_json(max_version)
        return self.json_package.copy()

    def check_valid_tgz(self, tgz_name: str) -> bool:
        version_smash = self.package_name.split('/')[-1] + "-"
        version = tgz_name.split(version_smash)[-1]

        if 'time' not in self.json_package:
            return False
        time_version = self.json_package['time']
        if self.check_date_release(time_version[version]):
            return True
        else:
            return False

    def get_date_upload_package(self, moratorium: bool = True) -> dict:
        if moratorium:
            self.get_repo_corrected_json()
        if 'error' in self.json_package:
            return {"error": "Not found"}
        return self.json_package['time'].copy()


class Pipe(Base):

    def get_repo_pypi_json(self) -> dict:
        if self.package_name:
            url = self.add_url_org_and_path('pypi', self.package_name, 'json')
            json_package = self.get_repo_json(url)
            return json_package
        else:
            return {"error": "Not self.package_name object"}

    @staticmethod
    def __get_correct_url_from_platform_package(platform_version: dict) -> str:
        url = platform_version['url']
        if url[:8] != r'https://':
            url = r'https://' + platform_version['url']
        return url

    @staticmethod
    def __get_date_upload_from_platform_package(platform_version: dict) -> str:
        return platform_version['upload_time']

    def __get_correct_from_platform_package(self, all_platform_version: dict,
                                            type_return: str = 'url',
                                            check_date_release: bool = True) -> dict:
        if type_return == 'url':
            function_result = self.__get_correct_url_from_platform_package
        elif type_return == 'date':
            function_result = self.__get_date_upload_from_platform_package
        else:
            function_result = None
        valid_package: dict = {}
        for platform_version in all_platform_version:
            date_release = platform_version['upload_time_iso_8601']
            if check_date_release:
                result_check_date: bool = self.check_date_release(date_release=date_release)
            else:
                result_check_date: bool = True
            if not result_check_date:
                continue
            filename = platform_version['filename']
            valid_package[filename] = function_result(platform_version)
        return valid_package

    def get_repo_corrected_json(self, type_return: str = 'url',
                                check_date_release: bool = True) -> dict:
        return_options: list = ['url', 'date']
        if type_return not in return_options:
            return {}
        valid_package: dict = {}
        json_package = self.get_repo_pypi_json()
        if 'error' in json_package:
            return {}
        version_release = json_package['releases']
        for full_version in version_release:
            all_platform_version = version_release[full_version]
            valid_package.update(self.__get_correct_from_platform_package(all_platform_version,
                                                                          type_return, check_date_release))
        return valid_package

    def get_date_upload_package(self, moratorium: bool = True) -> dict:
        if moratorium:
            result = self.get_repo_corrected_json(type_return='date')
        else:
            result = self.get_repo_corrected_json(type_return='date', check_date_release=False)

        if not result:
            return {"error": "Not found"}
        return result
