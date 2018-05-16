# -*- coding: utf-8 -*-
from flask import Flask, g, redirect, make_response, jsonify
from flask_session import Session
from flask_cors import CORS
import os

# Define the WSGI application object
app = Flask(__name__, static_url_path='/static', template_folder='/static/front')
app.static_folder = 'static'
app.template_folder = 'static/front'

#: Configurations
import configs

if os.environ.get('PURPOSE') == 'PROD':
    app.config.from_object(configs.ProdConfig)
elif os.environ.get('PURPOSE') == 'DEV':
    app.config.from_object(configs.DevConfig)
else:
    app.config.from_object(configs.Config)

#: Swagger
#Swagger(app)

#: Flask-Session
Session(app)

#: Flask-CORS
cors = CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": "true"}})

#: DB 연결 - configs에 설정해서 바로 연결해서 쓸 수 있도록 했습니다.

#################################### 모듈 연결시키기 ####################################

# API Version
versions = ['/api/v1']

## Example

#from app.auth.urls import auth
#app.register_blueprint(auth, url_prefix='/api/v1/auth')

#: 등록된 url 확인하기
print(app.url_map)

#####################################################################################



@app.before_request
def before_request():
    """
    모든 API 실행 전 실행하는 부분
    """
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

    if '/api' in request.environ['PATH_INFO']:
        is_ok = common.ddos_check_and_write_log()
        if is_ok is False:
            return make_response(jsonify(result_en='Blocked connection'
                                         , result_ko='접속이 차단되었습니다'
                                         , result=503), 503)


@app.teardown_request
def teardown_request(exception):
    """
    모든 API 실행 후 실행하는 부분. 여기서는 DB 연결종료.
    """
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify(result_ko='존재하지 않는 페이지입니다'
                                 , result_en='Not Found!'
                                 , result=404), 404)


@app.errorhandler(401)
def not_unauthorized(error):
    return make_response(jsonify(result_ko='인증되지 않음'
                                 , result_en='Unauthenticated'
                                 , result=401), 401)


@app.errorhandler(403)
def forbidden(error):
    # return abort(403)
    return make_response(jsonify(result_ko='접근 금지!'
                                 , result_en='Forbidden!'
                                 , result=403), 403)


