# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:48:01 2020

@author: ShangFR

import redis

pool = redis.ConnectionPool(host='localhost', port=6379,db=1)
red = redis.Redis(connection_pool=pool)
red.set('abcs', "exp", px = 100)



import os
os.chdir("C:\\Users\\ShangFR\\Desktop\\vue-form-making\\myflask")   #修改当前工作目录
os.getcwd()
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from script.models import * #User,build_sample_db

from log.log_test import Logger

Logger('log\\error.log', level='error').logger.error('error')
log = Logger('log\\all.log',level='debug')
log.logger.debug('debug')
log.logger.info('info')
log.logger.warning('警告')
log.logger.error('报错')
log.logger.critical('严重')
   

app = Flask(__name__)
api = Api(app)
#import config
#app.config.from_object(config)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)

parser = reqparse.RequestParser()
parser.add_argument('task')
parser.add_argument('auth_key', type=str)
parser.add_argument('auth_value', type=str)

tokens = {}

def create_token(api_user):
    '''
    生成token
    :param api_user:用户id
    :return: token
    '''
    
    #第一个参数是内部的私钥，这里写在共用的配置信息里了，如果只是测试可以写死
    #第二个参数是有效期(秒)
    s = Serializer(app.config["SECRET_KEY"],expires_in=3600)
    #接收用户id转换与编码
    token = s.dumps({"id":api_user}).decode("ascii")
    tokens[api_user] = token
    return token


TODOS = {
    'todo1': {'task': 'hello python'},
    'todo2': {'task': 'hello java'},
    'todo3': {'task': 'hello flask'},
}

# 检索是否有资源
def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="所查资源不存在".format(todo_id))


def not_found():
    abort(404, message={'error': 'Not Find auth_type'})


def auth_error():
    abort(404, message={"error": "username or password is None"})

@token_auth.verify_token
def verify_token(token):
    '''
    校验token
    :param token: 
    :return: 用户信息 or None
    '''
    
    #参数为私有秘钥，跟上面方法的秘钥保持一致
    s = Serializer(app.config["SECRET_KEY"])
    try:
        #转换为字典
        data = s.loads(token)
    except Exception:
        return None
    #拿到转换后的数据，根据模型类去数据库查询用户信息
    if token in tokens.values():
        return True   
    elif data["id"] in tokens.keys():
        abort(401, message={'error': "Your token is expired"})
        return False
    return False


@token_auth.error_handler
def unauthorized():
    """
    认证失败
        flask 需要以return 这种方式返回自定义异常
            return make_response(jsonify({'error': 'Not Find'}), 401)
        flask_restful 则修改abort方式返回自定义异常
            abort(401, message={'error': 'Unauthorized access'})
    :return:
    """
    abort(401, message={'error': 'Unauthorized access (auth_type: token)'})


@basic_auth.verify_password
def verify_password(username, password):
    """
    用户名密码认证
        curl -u Tom:111111 -i -X GET http://localhost:5000/
    :param username:
    :param password:
    :return:
    """
    user = User.query.filter_by(username = username).first()
    
    if not user or not user.check_password(password):
        abort(401, message={'error': '用户名或密码错误'})
        return False
    return True


@basic_auth.error_handler
def unauthorized2():
    abort(401, message={'error': 'Unauthorized access (auth_type: name)'})


class AuthSafety(Resource):
    """认证用户注册"""

    def post(self, auth_type):
        """
        注册新用户
        :param auth_type: name：姓名密码方式注册；token：token方式注册
        :return:
        """
        args = parser.parse_args()
        auth_key = args['auth_key']
        auth_value = args['auth_value']
        if auth_key is None or auth_value is None:
            auth_error()
        if auth_type == 'name':
            if User.query.filter_by(username = auth_key).first() is not None:
                abort(400, message={'error': 'existing user'}) # 
                
            user = User(username = auth_key,
                        password = generate_password_hash(auth_value))
            db.session.add(user)
            db.session.commit()
            token = create_token(auth_key)
            #with open("pws.txt", 'a', encoding='utf-8') as f:
            #   f.write(str({'username': auth_key, 'password': generate_password_hash(auth_value)})+'\n')
            return {"UserName": auth_key, "Token": token, "type": "name"}, 200
        elif auth_type == 'update_token':
            user = User.query.filter_by(username = auth_key).first()
            if not user or not user.check_password(auth_value):
                abort(400, message={'error': 'wrong user or password'}) #
            else:
                token = create_token(auth_key)
                return {"UserName": auth_key, "Token": token}, 200
        else:
            not_found()
   


    def get(self, auth_type):
        data = User.query.all()
        return str(data)


class Todo(Resource):
    decorators = [multi_auth.login_required]  # flask_restful 安全认证方式，类似于flask注解，全局认证
    '''采用flask注解方式认证，那个方法需要认证，则将注解加到此处'''

    # @basic_auth.login_required  # 用户名密码认证方式
    # @token_auth.login_required  # token认证方式
    # @multi_auth.login_required  # 两种综合认证方式，满足其一即可
    def get(self, todo_id):
        """
        curl -X GET -H "Authorization: Bearer secret-token-1" http://localhost:5000/todos/todo1
        curl -u Tom:111111 -i -X GET http://localhost:5000/todos/todo1
        :param todo_id: todo1,检索关键字
        :return:
        """
        abort_if_todo_doesnt_exist(todo_id)  # 如果资源不存在
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


class TodoList(Resource):
    decorators = [multi_auth.login_required]

    def get(self):
        if len(TODOS) == 0:
            not_found()  # 无资源
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


# 设置路由规则
api.add_resource(AuthSafety, '/auth/<auth_type>')
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')


if __name__ == '__main__':
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()
    app.run(debug=True)
