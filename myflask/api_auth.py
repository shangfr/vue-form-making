# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:48:01 2020

@author: ShangFR

"""
import sys
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

app = Flask(__name__)
api = Api(app)
#import config
#app.config.from_object(config)
app.config.from_pyfile('C:\\Users\\ShangFR\\Desktop\\vue-form-making\\myflask\\config.py')
db = SQLAlchemy(app)


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)

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
    abort(404, message={'error': 'Not Find'})


def auth_error():
    abort(404, message={"error": "username or password is None"})


parser = reqparse.RequestParser()
parser.add_argument('task')
parser.add_argument('auth_key', type=str)
parser.add_argument('auth_value', type=str)



tokens = {
    "secret-token-1": "John",
    "secret-token-2": "Susan"
}

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
    if data["id"] in tokens.keys():
        return True
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
    abort(401, message={'error': 'Unauthorized access'})


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
        print('用户名或密码错误')
        return False
    return True


@basic_auth.error_handler
def unauthorized():
    abort(401, message={'error': 'Unauthorized access'})



# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)



class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name
    __repr__ = __str__


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)
     
    def set_password(self, password):
        self.password = generate_password_hash(password)
     
    def check_password(self, password):
        return check_password_hash(self.password, password)

#    def __str__(self):
#        return '(User: %s, %s)' %(self.username, self.password)
#    __repr__ = __str__
    
def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        db.session.add(User(
            username='Admin',
            email='admin@qq.com',
            password=generate_password_hash('admin'),
            roles=[user_role, super_user_role]
        ))

        usernames = [
            'Harry', 'Amelia', 'Oliver'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel'
        ]

        for i in range(len(usernames)):
            tmp_email = usernames[i].lower() + "." + last_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            db.session.add(User(
                username=usernames[i],
                last_name=last_names[i],
                email=tmp_email,
                password=generate_password_hash(tmp_pass),
                roles=[user_role, ]
            ))
        db.session.commit()
    return



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
        if User.query.filter_by(username = auth_key).first() is not None:
            abort(400) # existing user
            
        user = User(username = auth_key,
        password = auth_value)
        db.session.add(user)
        db.session.commit()
        
        if auth_type == 'name':
            #with open("pws.txt", 'a', encoding='utf-8') as f:
            #   f.write(str({'username': auth_key, 'password': generate_password_hash(auth_value)})+'\n')
            return {"UserName": auth_key, "PassWord": auth_value, "type": "name"}, 200
        elif auth_type == 'token':
            token = create_token(auth_key)
            return {"UserName": auth_key, "Token": token}, 200
        else:
            auth_error()
   


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
