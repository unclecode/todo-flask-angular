__author__ = 'unclecode'
from flask import Blueprint, url_for
from flask_restful import Resource, reqparse, marshal, Api, inputs

import json, os, re, time
from app.libs import *

from app import tokenAuth, app
from app.models.task import Task
from app.models.validators import *

from datetime import datetime, timedelta

api_task_note = Blueprint('api_task_note', __name__)

post_parser = reqparse.RequestParser(bundle_errors=True)
post_parser.add_argument('content', type=str, required=True)

filter_parser = reqparse.RequestParser(bundle_errors=True)
filter_parser.add_argument('query', type=str, default = '')

note_fields = {
    'note': fields.String,
    'time_created' : fields.Float,
    'time_updated' : fields.Float,
    'index': fields.Integer
}

taskNoteListApiLimiter = get_shared_limit("taskNoteListApi", app, "1000/day;500/hour;100/minute;20/second")

class TaskNoteListApi(Resource):
    #method_decorators = [tokenAuth.login_required, taskListApiLimiter]
    method_decorators = [taskNoteListApiLimiter]

    def __init__(self):
        pass

    def get(self, owner, task_id):
        task = Task.objects.get_or_404(owner=owner, id=task_id, removed=False)
        return {
            'result':True,
            'count': len(task.notes),
            'owner': owner,
            'task_id': task_id,
            'notes': [marshal(t.to_dict(), note_fields) for t in task.notes]
        }

    def post(self, owner, task_id):
        task = Task.objects.get_or_404(owner=owner, id=task_id, removed=False)
        args = post_parser.parse_args()
        note =task.add_note(args['content'])
        return {'result':True, 'note': marshal(note.to_dict(), note_fields)}, 201


class TaskNoteApi(Resource):
    #method_decorators = [tokenAuth.login_required, taskNoteListApiLimiter]
    method_decorators = [taskNoteListApiLimiter]

    def __init__(self):
        pass

    def get(self, owner, task_id, index):
        task = Task.objects.get_or_404(owner=owner, id=task_id, removed=False)
        note = task.get_note_by_index(index)
        return {'result':True, 'note': marshal(note.to_dict() or {}, note_fields)}, 201

    def put(self, owner, task_id, index):
        args = post_parser.parse_args()
        task = Task.objects.get_or_404(owner=owner, id=task_id, removed=False)
        task.set_note_by_index(index, args['content'])
        return {'result':True, 'task': marshal(task.get_note_by_index(index).to_dict() or {}, note_fields)}, 201

    def delete(self, owner, task_id, index):
        task = Task.objects.get_or_404(owner=owner, id=task_id, removed=False)
        task.remove_note(index)
        return {"result": True, 'task_id': task_id, 'index': index}

api = Api(api_task_note)
api.add_resource(TaskNoteListApi, '/<string:owner>/<string:task_id>', endpoint='notes')
api.add_resource(TaskNoteApi, '/<string:owner>/<string:task_id>/<int:index>', endpoint='note')
