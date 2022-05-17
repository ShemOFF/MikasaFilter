from flask import Flask, request, redirect, render_template, make_response, jsonify
import gzip

from base import NPM, Pipe
from project_config import NPM_ORG_REPO_URL, NPM_ORG_DATE_TIME_PATTERN, NPM_LOCAL_REPO, \
    PYPI_ORG_REPO_URL, PYPI_ORG_DATE_TIME_PATTERN, PYPI_LOCAL_REPO

app = Flask(__name__)


@app.route(f'/')
def main_index():
    return render_template('main.html')


@app.route(f'/{NPM_LOCAL_REPO}/<path:package>', methods=['GET'])
def npm_package(package: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL, date_pattern=NPM_ORG_DATE_TIME_PATTERN)

    valid_package: dict = npm_checker.get_repo_corrected_json(package)
    return make_response(jsonify(valid_package), 200)


@app.route(f'/{NPM_LOCAL_REPO}/<path:package>/-/<string:tgz>.tgz', methods=['GET'])
def npm_tgz(package: str, tgz: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL, date_pattern=NPM_ORG_DATE_TIME_PATTERN)

    tgz_path: str = f'{package}/-/{tgz}.tgz'
    url_repo: str = npm_checker.add_url_org_and_path(tgz_path)
    if npm_checker.check_valid_tgz(package=package, tgz_name=tgz):
        return redirect(url_repo, code=302)
    else:
        return 'error'


@app.route(f'/{NPM_LOCAL_REPO}/-/npm/v1/security/<path:sec>', methods=['POST'])
def npm_audit(sec: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL, date_pattern=NPM_ORG_DATE_TIME_PATTERN)

    security_path: str = f'-/npm/v1/security/{sec}'
    url_repo: str = npm_checker.add_url_org_and_path(security_path)
    data: bytes = (gzip.decompress(request.data))
    post_request: dict = npm_checker.post_repo_json(url_repo, data=data)
    return make_response(jsonify(post_request), 200)


@app.route(f'/{PYPI_LOCAL_REPO}/simple/<string:package>/', methods=['GET'])
def pypi_simple(package: str):
    pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL, date_pattern=PYPI_ORG_DATE_TIME_PATTERN)

    valid_package: dict = pypi_checker.get_repo_corrected_json(package)
    return render_template('pypi_simple.html', package=package, valid_package=valid_package)


# @app.route(f'/{PYPI_LOCAL_REPO}/packages/<string:package>/', methods=['GET'])
# def pypi_package(package: str):
#     pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL, date_pattern=PYPI_ORG_DATE_TIME_PATTERN)
#
#     valid_package: dict = pypi_checker.get_repo_corrected_json(package)
#     return render_template('pypi_simple.html', package=package, valid_package=valid_package)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
