__author__ = 'unclecode'
# Import flask dependencies
from flask import Blueprint, render_template, abort, session, redirect, request
from flask_restful import Resource, reqparse, fields, marshal, marshal_with, Api
from flask_httpauth import HTTPBasicAuth
import json, os, re, time


from app.models.user import User
from app.models.validators import *

api_user = Blueprint('api_user', __name__)

# dir_path = os.path.dirname(os.path.realpath(__file__))
# data = json.loads(open( dir_path + '/data.json').read())

post_parser = reqparse.RequestParser(bundle_errors=True)
post_parser.add_argument('first_name', type = str) #,  required = True, dest = 'final name in db', location = 'form|json|cookie|', help = "Message comes in error")
post_parser.add_argument('last_name', type = str)
post_parser.add_argument('age', type = int)
post_parser.add_argument('email', type = email_validator, required = True)
post_parser.add_argument('gender', type = str, choices = ['male', 'female'], help = "User gender, male or female")
post_parser.add_argument('pwd', type = str)


class ReadableTime(fields.Raw):
    def format(self, value):
        return [value, time.ctime(value)]

user_fields = {
    'first_name': fields.String,
    'last_name': fields.String,
    'full_name': fields.FormattedString('{first_name} {last_name}'),
    'email': fields.String(attribute='_id'),
    'gender': fields.String,
    'time':{
      'created':  ReadableTime(attribute='time_created'), #[ReadableTime(attribute='time_created'), fields.Float(attribute='time_created')],
      'updated':  ReadableTime(attribute='time_created'), #[ReadableTime(attribute='time_updated'), fields.Float(attribute='time_updated')],
    },
    'links': {
        'user': fields.Url('api_user.users', absolute= True, scheme="http"),
        #'tasks': fields.Url('api_task.tasks', absolute = True, scheme = "http")
    }
}

class UserListApi(Resource):
    def __init__(self):
        pass

    def get(self):
        users = User.objects().exclude('pwd').as_pymongo()
        return [marshal(t, user_fields) for t in users]
        pass

    def post(self):
        args = post_parser.parse_args()
        # args.pop('uri', 0)
        # data['users'].append(args)
        return {'users': marshal(args, user_fields)}, 201
    pass

class UserApi(Resource):
    def __init__(self):
        pass

    def get(self, email):
        user = User.objects.get_or_404(email=email).to_dict()
        return {'users': marshal(user, user_fields) }, 201

    def put(self, email):
        args = post_parser.parse_args()
        user = User.objects.get_or_404(email=email)
        for k, v in args.items():
            if v:
                setattr(user, k, v)
        user.save()
        return {'user':marshal(user.to_dict(), user_fields)}, 201

    def delete(self, email):
        user = User.objects.get_or_404(email=email)
        user.delete()
        return {"result":True}


api = Api(api_user)
api.add_resource(UserListApi, '/', endpoint = 'users')
api.add_resource(UserApi, '/<string:email>', endpoint = 'user')