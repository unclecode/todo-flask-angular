__author__ = 'unclecode'
from flask import Blueprint, url_for, render_template, abort, session, redirect, request
from flask_restful import Resource, reqparse, marshal, Api, inputs

import json, os, re, time
from app.lib import *

from app import tokenAuth, app
from app.models.task import Task
from app.models.validators import *

from datetime import datetime, timedelta

api_task = Blueprint('api_task', __name__)

post_parser = reqparse.RequestParser(bundle_errors=True)
post_parser.add_argument('content', type=str, required=True)
post_parser.add_argument('tags', type=str, action='append')
post_parser.add_argument('duration', type=int)
post_parser.add_argument('duration_type', type=str)
post_parser.add_argument('type', type=str, default = "task")
post_parser.add_argument('owner', type=email_validator, required=True)
post_parser.add_argument('status', type=str, choices=['backlog', 'todo', 'progress', 'done', 'delayed'])


filter_parser = reqparse.RequestParser(bundle_errors=True)
filter_parser.add_argument('page', type=int, default = 0)
filter_parser.add_argument('stage', type=str, default = '')
filter_parser.add_argument('flag', type=str, default = '')
filter_parser.add_argument('type', type=str, default = '')
filter_parser.add_argument('std', type=str, default = '')
filter_parser.add_argument('end', type=str, default = '')
filter_parser.add_argument('query', type=str, default = '')
filter_parser.add_argument('delayed', type=inputs.boolean, default = False)
filter_parser.add_argument('sortedBy', type=str, default = '-time_updated')

put_parser = post_parser.copy()
for arg in put_parser.args:
    arg.required = False


task_fields = {
    'task_id': fields.String(attribute='id'),
    'title': fields.String,
    'content': fields.String,
    'owner': fields.String,
    'status': fields.String,
    'tags': fields.List(fields.String),
    'type': fields.String(default='task'),
    'notes_count': fields.Integer(default=0),
    #'notes': fields.List(fields.Nested(note_fields)),
    'time': {
        'duration': fields.Float,
        'duration_hour': fields.Float,
        'left_hours': fields.Float,
        'duration_type': fields.String,
        'delayed': fields.Boolean,
        'created': ReadableTime(attribute='time_created'),
        'updated': ReadableTime(attribute='time_updated'),
    },
    'links': {
        'task': fields.Url('api_task.task', absolute=True, scheme="http")
    }
}

taskListApiLimiter = get_shared_limit("taskListApi", app, "1000/day;500/hour;100/minute;20/second")

class TaskListApi(Resource):
    #method_decorators = [tokenAuth.login_required, taskListApiLimiter]
    method_decorators = [taskListApiLimiter]

    def __init__(self):
        pass

    def get(self, owner):
        args = filter_parser.parse_args()
        page_no = args['page'] # int(request.args.get('page', 0))
        status = args['stage'] # request.args.get('stage', '')
        dateFlag = args['flag'] # request.args.get('flag', '') # today, week, month, custom
        startDate = args['std'] # request.args.get('std', '') # today, week, month, custom
        endDate = args['end']# request.args.get('snd', '') # today, week, month, custom
        query = args['query'] # request.args.get('query', '') # today, week, month, custom
        onlyDelayed = args['delayed'] # request.args.get('delayed', '') # today, week, month, custom
        sortedBy = args['sortedBy']# request.args.get('sortedBy', '-time_updated') # today, week, month, custom


        criteria = {
            'owner': owner,
            'removed':False
        }
        taskCount  = {}
        if status:
            criteria.update({
                'status__in' : [s.strip() for s in status.split(',')]
            })
        if dateFlag:
            d1 = datetime.now()
            today_start = d1 - timedelta(hours=d1.hour, minutes=d1.minute, seconds=d1.second)
            if dateFlag == 'today':
                criteria.update({
                    'time_updated__gte':time.mktime(today_start.timetuple()),
                    'time_updated__lte':time.time(),
                })
            elif dateFlag == 'week':
                criteria.update({
                    'time_updated__gte':time.mktime((today_start - timedelta(days=d1.weekday())).timetuple()),
                    'time_updated__lte':time.time(),
                })
                pass
            elif dateFlag == 'month':
                criteria.update({
                    'time_updated__gte':time.mktime((today_start - timedelta(days=d1.day)).timetuple()),
                    'time_updated__lte':time.time(),
                })
                pass
            elif dateFlag == 'custom':
                criteria.update({
                    'time_updated__gte':startDate,
                    'time_updated__lte':endDate,
                })
                pass
        tags = [i[1:] for i in query.split() if i.startswith("#")]
        if tags:
            criteria.update({
                'tags__all' : tags
            })
            for t in tags:
                query = re.sub('\#' + t, "", query).strip()

        if onlyDelayed:
            criteria['delayed'] = True


        if not query:
            tasks = Task.objects(**criteria).order_by( sortedBy).skip(page_no*10).limit(10).as_pymongo()
        else:
            regx = re.compile(query, re.IGNORECASE)
            criteria.update({
                "content": regx,
                "notes.note": regx
            })
            #tasks = Task.objects(**criteria).search_text(query).skip(page_no*10).limit(10).as_pymongo()
            tasks = Task.objects(**criteria).order_by(sortedBy).skip(page_no*10).limit(10).as_pymongo()

        criteria.pop('delayed', 0)
        taskCount['total'] = Task.objects(**criteria).count()
        criteria['delayed'] = True
        taskCount['delayed'] = Task.objects(**criteria).count()


        for t in tasks:
            t['id'] = t['_id']
            t.pop('_id', 0)
            t['title'] = t['content'][:10] + '...'
            t['notes_count'] = len(t['notes'])
        return {
            'result':True,
            'count': taskCount,
            'tasks': [marshal(t, task_fields) for t in tasks],
            'page': page_no,
            'nextPage': "{url}?page={next_page}{status}".format(
                url = url_for('api_task.tasks',  owner = owner),
                next_page = page_no + 1,
                status = ("&status=" + status) if status else ''
            )
        }

    def post(self, owner):
        args = post_parser.parse_args()
        new_task = Task(**args)
        new_task.calculate_hour_duration()
        new_task.calculate_left()
        new_task.save()
        current_user.add_tag(new_task.tags)
        d = new_task.to_dict()
        d['title'] = d['content'][:10] + '...'
        return {'result':True, 'task': marshal(d, task_fields)}, 201


taskApiLimiter = get_shared_limit("taskApi", app, "1000/day;500/hour;100/minute;20/second")

class TaskApi(Resource):
    method_decorators = [tokenAuth.login_required, taskApiLimiter]

    def __init__(self):
        pass

    def get(self, owner, id):
        task = Task.objects.get_or_404(owner=owner, id=id, removed=False).to_dict()
        task['notes_count'] = len(task['notes'])
        return {'result':True, 'task': marshal(task, task_fields)}, 201

    def put(self, owner, id):
        args = put_parser.parse_args()
        task = Task.objects.get_or_404(owner=owner, id=id)
        for k, v in args.items():
            if k not in ['owner', 'task_id'] and v:
                setattr(task, k, v)
        task.time_updated = time.time()
        task.save()
        return {'result':True, 'task': marshal(task.to_dict(), task_fields)}, 201

    def delete(self, owner, id):
        task = Task.objects.get_or_404(owner=owner, id=id)
        task.removed = True
        task.save()
        #task.delete()
        return {"result": True, 'task_id': id}

class TaskCountApi(Resource):
    method_decorators = [tokenAuth.login_required, taskApiLimiter]

    def __init__(self):
        pass

    def get(self, owner):
        result = {}
        for stage in ['backlog', 'todo', 'progress', 'done']:
            result[stage] = {
                'total': Task.objects(owner=owner, status=stage).count(),
                'delayed': Task.objects(owner=owner, status=stage, delayed=True).count()
            }
        return {'result':True, 'stat': result}, 201



api = Api(api_task)
api.add_resource(TaskListApi, '/<string:owner>', endpoint='tasks')
api.add_resource(TaskApi, '/<string:owner>/<string:id>', endpoint='task')
#api.add_resource(TaskCountApi, '/<string:owner>', endpoint='taskstat')
