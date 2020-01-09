# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 15:22:09 2020

@author: ShangFR
"""

import time
import pandas as pd 
import json
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource,request
from flask_cors import CORS

import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)

app = Flask(__name__)
CORS(app, supports_credentials=True) 
api = Api(app)

def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')

# Todo
TODOS = {
    'todo1': {'task': 'Data filter'},
    'todo2': {'task': 'Sorts users'},
    'todo3': {'task': 'profit!'},
}
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        if todo_id == 'todo1':
            data_filtered()
        elif todo_id == 'todo2':
            user_filtered()
        else:
            print('no task')
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

# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201

class Todoform(Resource):
    def get(self):
        return 'aa'

    def post(self):
        p_dict=request.json
        print(p_dict['widgetForm'])
        with open('forms/data.json','w',encoding='utf-8') as f:
            f.write(p_dict['widgetForm'])
        return 'ok', 201

class Todohtml(Resource):    
    def post(self):
        p_dict=request.json
        print(p_dict['htmlTemplate'])
        with open('html/form.html','w',encoding='utf-8') as f:
            f.write(p_dict['htmlTemplate'])
        return 'ok', 201

class Todofill(Resource):    
    def post(self):
        p_dict=request.json
        print(p_dict)
        with open('fillin/result.json','w',encoding='utf-8') as f:
            json.dump(p_dict,f,ensure_ascii=False)
        return 'ok', 201
# 从文件读取数据
#with open('C:\\Users\\ShangFR\\Desktop\\rankmodel\\data.json','r',encoding='utf-8') as f:
#    data = json.load(f)

#数据

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')
api.add_resource(Todoform, '/form')
api.add_resource(Todohtml, '/form_html')
api.add_resource(Todofill, '/fillin')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)