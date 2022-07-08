from flask import Flask, request, redirect, render_template, make_response, jsonify
import gzip

from base import NPM, Pipe
from project_config import NPM_ORG_REPO_URL, NPM_ORG_DATE_TIME_PATTERN, NPM_LOCAL_REPO, \
    PYPI_ORG_REPO_URL, PYPI_ORG_DATE_TIME_PATTERN, PYPI_LOCAL_REPO
app = Flask(__name__)


@app.route(f'/')
def main_index():
    return render_template('main.html')


# NPM:

@app.route(f'/{NPM_LOCAL_REPO}/date-upload-moratorium/<path:package>', methods=['GET'])
def npm_date_upload_moratorium(package: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      package_name=package)

    valid_package: dict = npm_checker.get_date_upload_package()
    return render_template('date_upload_package.html', type_package=f'Moratorium({npm_checker.moratorium_date})',
                           package=package, valid_package=valid_package)


@app.route(f'/{NPM_LOCAL_REPO}/<string:custom_date>/date-upload-moratorium/<path:package>', methods=['GET'])
def npm_date_upload_custom_date_moratorium(custom_date: str, package: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      custom_moratorium_date=custom_date,
                      package_name=package)

    if 'Error' in npm_checker.moratorium_date:
        return npm_checker.moratorium_date

    valid_package: dict = npm_checker.get_date_upload_package()
    return render_template('date_upload_package.html', type_package=f'Moratorium({npm_checker.moratorium_date})',
                           package=package, valid_package=valid_package)


@app.route(f'/{NPM_LOCAL_REPO}/date-upload-moratorium/json/<path:package>', methods=['GET'])
def npm_date_upload_moratorium_json(package: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      package_name=package)

    valid_package: dict = npm_checker.get_date_upload_package()
    return make_response(jsonify(valid_package), 200)


@app.route(f'/{NPM_LOCAL_REPO}/<string:custom_date>/date-upload-moratorium/json/<path:package>', methods=['GET'])
def npm_date_upload_custom_date_moratorium_json(custom_date: str, package: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      custom_moratorium_date=custom_date,
                      package_name=package)

    if 'Error' in npm_checker.moratorium_date:
        return npm_checker.moratorium_date

    valid_package: dict = npm_checker.get_date_upload_package()
    return make_response(jsonify(valid_package), 200)


@app.route(f'/{NPM_LOCAL_REPO}/date-upload-all/<path:package>', methods=['GET'])
def npm_date_upload_all(package: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      package_name=package)

    valid_package: dict = npm_checker.get_date_upload_package(moratorium=False)
    return render_template('date_upload_package.html', type_package='All',
                           package=package, valid_package=valid_package)


@app.route(f'/{NPM_LOCAL_REPO}/date-upload-all/json/<path:package>', methods=['GET'])
def npm_date_upload_all_json(package: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      package_name=package)

    valid_package: dict = npm_checker.get_date_upload_package(moratorium=False)
    return make_response(jsonify(valid_package), 200)


@app.route(f'/{NPM_LOCAL_REPO}/package/<path:package>', methods=['GET'])
def npm_package(package: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      package_name=package)

    valid_package: dict = npm_checker.get_repo_corrected_json()
    return make_response(jsonify(valid_package), 200)


@app.route(f'/{NPM_LOCAL_REPO}/<string:custom_date>/package/<path:package>', methods=['GET'])
def npm_custom_date_package(custom_date: str, package: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      custom_moratorium_date=custom_date,
                      package_name=package)

    if 'Error' in npm_checker.moratorium_date:
        return npm_checker.moratorium_date

    valid_package: dict = npm_checker.get_repo_corrected_json()
    return make_response(jsonify(valid_package), 200)


@app.route(f'/{NPM_LOCAL_REPO}/package/<path:package>/-/<string:tgz>.tgz', methods=['GET'])
def npm_tgz(package: str, tgz: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      package_name=package)

    tgz_path: str = f'{package}/-/{tgz}.tgz'
    url_repo: str = npm_checker.add_url_org_and_path(tgz_path)
    if npm_checker.check_valid_tgz(tgz_name=tgz):
        return redirect(url_repo, code=302)
    else:
        return 'error'


@app.route(f'/{NPM_LOCAL_REPO}/<string:custom_date>/package/<path:package>/-/<string:tgz>.tgz', methods=['GET'])
def npm_custom_date_tgz(custom_date: str, package: str, tgz: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      package_date_pattern=NPM_ORG_DATE_TIME_PATTERN,
                      custom_moratorium_date=custom_date,
                      package_name=package)

    if 'Error' in npm_checker.moratorium_date:
        return npm_checker.moratorium_date

    tgz_path: str = f'{package}/-/{tgz}.tgz'
    url_repo: str = npm_checker.add_url_org_and_path(tgz_path)
    if npm_checker.check_valid_tgz(tgz_name=tgz):
        return redirect(url_repo, code=302)
    else:
        return 'error'


@app.route(f'/{NPM_LOCAL_REPO}/package/-/npm/v1/security/<path:sec>', methods=['POST'])
def npm_audit(sec: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL)

    security_path: str = f'-/npm/v1/security/{sec}'
    print(security_path)
    url_repo: str = npm_checker.add_url_org_and_path(security_path)
    data: bytes = (gzip.decompress(request.data))
    post_request: dict = npm_checker.post_repo_json(url_repo, data=data)
    return make_response(jsonify(post_request), 200)


@app.route(f'/{NPM_LOCAL_REPO}/<string:custom_date>/package/-/npm/v1/security/<path:sec>', methods=['POST'])
def npm_custom_date_audit(custom_date: str, sec: str):
    npm_checker = NPM(url_org_repo=NPM_ORG_REPO_URL,
                      custom_moratorium_date=custom_date)

    if 'Error' in npm_checker.moratorium_date:
        return npm_checker.moratorium_date

    security_path: str = f'-/npm/v1/security/{sec}'
    url_repo: str = npm_checker.add_url_org_and_path(security_path)
    data: bytes = (gzip.decompress(request.data))
    post_request: dict = npm_checker.post_repo_json(url_repo, data=data)
    return make_response(jsonify(post_request), 200)


# Pypi:


@app.route(f'/{PYPI_LOCAL_REPO}/date-upload-moratorium/<string:package>/', methods=['GET'])
def pypi_date_upload_moratorium(package: str):
    pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL,
                        package_date_pattern=PYPI_ORG_DATE_TIME_PATTERN,
                        package_name=package)

    valid_package: dict = pypi_checker.get_date_upload_package()
    return render_template('date_upload_package.html', type_package=f'Moratorium({pypi_checker.moratorium_date})',
                           package=package, valid_package=valid_package)


@app.route(f'/{PYPI_LOCAL_REPO}/<string:custom_date>/date-upload-moratorium/<string:package>/', methods=['GET'])
def pypi_date_upload_custom_date_moratorium(custom_date: str, package: str):
    pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL,
                        package_date_pattern=PYPI_ORG_DATE_TIME_PATTERN,
                        custom_moratorium_date=custom_date,
                        package_name=package)

    if 'Error' in pypi_checker.moratorium_date:
        return pypi_checker.moratorium_date

    valid_package: dict = pypi_checker.get_date_upload_package()
    return render_template('date_upload_package.html', type_package=f'Moratorium({pypi_checker.moratorium_date})',
                           package=package, valid_package=valid_package)


@app.route(f'/{PYPI_LOCAL_REPO}/date-upload-moratorium/json/<string:package>/', methods=['GET'])
def pypi_date_upload_moratorium_json(package: str):
    pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL,
                        package_date_pattern=PYPI_ORG_DATE_TIME_PATTERN,
                        package_name=package)

    valid_package: dict = pypi_checker.get_date_upload_package()
    return make_response(jsonify(valid_package), 200)


@app.route(f'/{PYPI_LOCAL_REPO}/<string:custom_date>/date-upload-moratorium/json/<string:package>/', methods=['GET'])
def pypi_date_upload_custom_date_moratorium_json(custom_date: str, package: str):
    pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL,
                        package_date_pattern=PYPI_ORG_DATE_TIME_PATTERN,
                        custom_moratorium_date=custom_date,
                        package_name=package)

    if 'Error' in pypi_checker.moratorium_date:
        return pypi_checker.moratorium_date

    valid_package: dict = pypi_checker.get_date_upload_package()
    return make_response(jsonify(valid_package), 200)


@app.route(f'/{PYPI_LOCAL_REPO}/date-upload-all/<string:package>/', methods=['GET'])
def pypi_date_upload_all(package: str):
    pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL,
                        package_date_pattern=PYPI_ORG_DATE_TIME_PATTERN,
                        package_name=package)

    valid_package: dict = pypi_checker.get_date_upload_package(moratorium=False)
    return render_template('date_upload_package.html', type_package=f'All',
                           package=package, valid_package=valid_package)


@app.route(f'/{PYPI_LOCAL_REPO}/date-upload-all/json/<string:package>/', methods=['GET'])
def pypi_date_upload_all_json(package: str):
    pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL,
                        package_date_pattern=PYPI_ORG_DATE_TIME_PATTERN,
                        package_name=package)

    valid_package: dict = pypi_checker.get_date_upload_package(moratorium=False)
    return make_response(jsonify(valid_package), 200)


@app.route(f'/{PYPI_LOCAL_REPO}/simple/<string:package>/', methods=['GET'])
def pypi_simple(package: str):
    pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL,
                        package_date_pattern=PYPI_ORG_DATE_TIME_PATTERN,
                        package_name=package)

    valid_package: dict = pypi_checker.get_repo_corrected_json()
    return render_template('pypi_simple.html', package=f'{package} ({pypi_checker.moratorium_date})',
                           valid_package=valid_package)


@app.route(f'/{PYPI_LOCAL_REPO}/<string:custom_date>/simple/<string:package>/', methods=['GET'])
def pypi_custom_date_simple(custom_date: str, package: str):
    pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL,
                        package_date_pattern=PYPI_ORG_DATE_TIME_PATTERN,
                        custom_moratorium_date=custom_date,
                        package_name=package)

    if 'Error' in pypi_checker.moratorium_date:
        return pypi_checker.moratorium_date

    valid_package: dict = pypi_checker.get_repo_corrected_json()
    return render_template('pypi_simple.html', package=f'{package} ({pypi_checker.moratorium_date})',
                           valid_package=valid_package)

# @app.route(f'/{PYPI_LOCAL_REPO}/packages/<string:package>/', methods=['GET'])
# def pypi_package(package: str):
#     pypi_checker = Pipe(url_org_repo=PYPI_ORG_REPO_URL, date_pattern=PYPI_ORG_DATE_TIME_PATTERN)
#
#     valid_package: dict = pypi_checker.get_repo_corrected_json(package)
#     return render_template('pypi_simple.html', package=package, valid_package=valid_package)


if __name__ == '__main__':
    # app.config['SERVER_NAME'] = 'localhost:5000'
    app.run(debug=False, host='0.0.0.0')

