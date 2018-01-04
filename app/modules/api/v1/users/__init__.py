__author__ = 'unclecode'
from flask import Blueprint, render_template, abort, session, redirect, request
from flask_restful import Resource, reqparse, fields, marshal, marshal_with, Api
import json, os, re, time

from app.lib import *
from app import tokenAuth, app, cache
from app.models.user import User
from app.models.validators import *

api_user = Blueprint('api_user', __name__)

post_parser = reqparse.RequestParser(bundle_errors=True)
post_parser.add_argument('first_name', type = str) #,  required = True, dest = 'final name in db', location = 'form|json|cookie|', help = "Message comes in error")
post_parser.add_argument('last_name', type = str, required = True)
post_parser.add_argument('age', type = int, required = True)
post_parser.add_argument('email', type = email_validator, required = True)
post_parser.add_argument('gender', type = str, choices = ['male', 'female'], help = "User gender, male or female")
post_parser.add_argument('pwd', type = str, required = True)

put_parser = post_parser.copy()
for arg in put_parser.args:
    arg.required = False

user_fields = {
    'first_name': fields.String,
    'last_name': fields.String,
    'full_name': fields.FormattedString('{first_name} {last_name}'),
    'email': fields.String(attribute='_id'),
    'gender': fields.String,
    'tags': fields.List(fields.String),
    'time':{
      'created':  ReadableTime(attribute='time_created'), #[ReadableTime(attribute='time_created'), fields.Float(attribute='time_created')],
      'updated':  ReadableTime(attribute='time_updated'), #[ReadableTime(attribute='time_updated'), fields.Float(attribute='time_updated')],
    },
    'links': {
        'user': fields.Url('api_user.users', absolute= True, scheme="http"),
        'tasks': fields.Url('api_task.tasks', absolute = True, scheme = "http")
    }
}


userListApiLimiter = get_shared_limit("userListApi", app, "1000/day;500/hour;100/minute;20/second")

class UserListApi(Resource):
    #method_decorators = [tokenAuth.login_required, userListApiLimiter]
    def __init__(self):
        pass

    @cache.cached(timeout=10, key_prefix='all_users')
    @tokenAuth.login_required
    @userListApiLimiter
    def get(self):
        users = User.objects().exclude('pwd').as_pymongo()
        for u in users:
            u['owner'] = u['_id']
        return {'users': [marshal(t, user_fields) for t in users]}
        pass

    @userListApiLimiter
    def post(self):
        args = post_parser.parse_args()
        if not User.objects(email=args['email']):
            new_user = User(**args)
            new_user.hash_pwd()
            new_user.generate_session_token()
            new_user.generate_active_account_token()
            new_user.generate_welcome_tasks()
            new_user.save()
            u = new_user.to_dict()
            u['owner'] = u['_id']
            return {'result': True, 'user': marshal(u, user_fields)}, 201
        else:
            return {'result':False, 'msg':'User already exists'}, 400
    pass

userApiLimiter = get_shared_limit("userApi", app, "1000/day;500/hour;100/minute;20/second")

class UserApi(Resource):
    method_decorators = [tokenAuth.login_required, userApiLimiter]
    def __init__(self):
        pass

    @cache.cached(timeout=10, key_prefix='one_user')
    def get(self, email):
        user = User.objects.get_or_404(email=email).to_dict()
        return {'result':True, 'user': marshal(user, user_fields) }, 201

    def put(self, email):
        args = put_parser.parse_args()
        user = User.objects.get_or_404(email=email)
        for k, v in args.items():
            if v:
                setattr(user, k, v)
        user.time_updated = time.time()
        user.save()
        return {'result':True, 'user':marshal(user.to_dict(), user_fields)}, 201

    def delete(self, email):
        user = User.objects.get_or_404(email=email)
        user.delete()
        return {"result":True}


api = Api(api_user)
api.add_resource(UserListApi, '/', endpoint = 'users')
api.add_resource(UserApi, '/<string:email>', endpoint = 'user')