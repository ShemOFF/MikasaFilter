import datetime

check_date = '18-02-2022'
check_date = datetime.datetime.strptime(check_date, '%d-%m-%Y')
UNIX_CHECK_DATETIME = datetime.datetime.timestamp(check_date)
del datetime
del check_date

NPM_ORG_REPO_URL = r'https://registry.npmjs.org/'
NPM_ORG_DATE_TIME_PATTERN = r'%Y-%m-%dT%H:%M:%S.%fZ'
NPM_LOCAL_REPO = 'npm-api'

PYPI_ORG_REPO_URL = r'https://pypi.org'
PYPI_ORG_DATE_TIME_PATTERN = r'%Y-%m-%dT%H:%M:%S.%fZ'
PYPI_LOCAL_REPO = r'pypi-api'
