__author__ = 'unclecode'
# Import flask dependencies
from flask import Blueprint, render_template, abort, session, redirect, jsonify, request
from flask.views import MethodView

from app import mongodb
import json, os
# Define the blueprint: 'XXX', set its url prefix: app.url/PREFIX
mod_user_api = Blueprint('user_api', __name__)

dir_path = os.path.dirname(os.path.realpath(__file__))

data = json.loads(open(dir_path + '/data.json').read())

class UserListApi(MethodView):
    def get(self):
        return jsonify( { "users" : data["users"] } ), 201
        pass
    def post(self):
        user_data = request.form.to_dict()
        data["users"].append(user_data)
        user_data.pop('pwd', 0)
        return jsonify({"user" : user_data}), 201


class UserApi(MethodView):
    def get(self, id):
        user = [t for t in data['users'] if t['id'] == id]
        if user:
            return jsonify({'user': user[0]}), 201
        else:
            return jsonify({}), 404
    def put(self, id):
        user = [t for t in data['users'] if t['id'] == id]
        if user:
            user_data = request.form.to_dict()
            user[0].update(user_data)
            return jsonify({'user': user[0]}), 201
        else:
            return jsonify({}), 404
        pass
    def delete(self, id):
        user = [t for t in data['users'] if t['id'] == id]
        if user:
            data['users'] = [t for t in data['users'] if t['id'] != id]
            return jsonify({'result': True}), 201
        else:
            return jsonify({'result': False}), 404
        pass

mod_user_api.add_url_rule('/', view_func=UserListApi.as_view('users'))
mod_user_api.add_url_rule('/<string:id>', view_func=UserApi.as_view('user'))

