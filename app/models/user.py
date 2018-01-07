__author__ = 'unclecode'
import sys, os, json, hashlib
import mongoengine, re, time
from flask_login import UserMixin
from app import db, app
from task import Task
from passlib.apps import custom_app_context as pwd_context

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

#db = mongoengine.connect("ktodo")
#_db = db.connect("ktodo")
#_db = db.connection.get_db()
#You can have access to pymongo just liket his
#_db.ktodo...


class User(db.DynamicDocument, UserMixin):
    # fields arguments http://docs.mongoengine.org/guide/defining-documents.html#field-arguments
    # field marked as primary_key will be replaced by object id then user.id returns it
    email = db.StringField( primary_key=True,  regex= re.compile(r'(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)',re.IGNORECASE) )
    first_name = db.StringField(default=None)
    last_name = db.StringField()
    age = db.IntField(min_value=10, max_value=80, default=20)
    tags = db.ListField(db.StringField())
    gender = db.StringField(choices=['male', 'female'])
    time_created = db.FloatField(default=time.time())
    time_updated = db.FloatField(default=time.time())
    pwd = db.StringField(min_length=6, required=True)
    session_token = db.StringField()
    account_active_token = db.StringField()
    authenticated = db.BooleanField(default=False)

    meta = {
        'collection':'users',
        'indexes': [
            'email',
            ('+first_name', '+last_name')
        ]
        # You can create subclass from User and all of them store their data in User collection! So not a new collection!
        # This is good, gv us inheritance abilities in coding part anf looks like inheritance, but actually uses same collection but different
        # object schema
        # http://docs.mongoengine.org/guide/defining-documents.html#document-inheritance
        ,'allow_inheritance': True
        #default ordering good for things like comments
        ,'ordering':['-time_updated']
    }

    def getMe(self):
        me = self.to_dict()
        me = {k:me[k] for k in me.keys() if k in ['_id', 'first_name', 'last_name', 'age', 'gender', 'tags']}
        me['email'] = me['_id']
        me.pop('_id', 0)
        me['account_verified'] = 'account_active_token' not in self
        return me

    def generate_session_token(self):
        self.session_token = os.urandom(24).encode('hex')

    def generate_active_account_token(self):
        self.account_active_token = os.urandom(10).encode('hex')

    def generate_welcome_tasks(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        tasks = json.loads(open(cur_dir + '/welcome_tasks.json').read())['tasks']
        for t in tasks:
            task = Task(
                content=t['content'],
                status=t['status'],
                owner=self.id,
                tags=t['tags'],
                duration_type = 'day',
                duration = 1
            )
            task.calculate_hour_duration()
            task.time_created = time.time()
            task.calculate_left()
            task.save()
        self.tags.append('welcome')

    def verify_account(self, token):
        if not self.is_account_verified() and self.account_active_token == token:
            self.update(unset__account_active_token=1)
            self.save()
            return True
        return False

    def is_account_verified(self):
        return 'account_active_token' not in self

    def hash_pwd(self):
        # self.pwd = pwd_context.encrypt(self.pwd)
        self.pwd = hashlib.sha1(self.pwd).hexdigest()

    def verify_pwd(self, pwd):
        return self.pwd == hashlib.sha1(pwd).hexdigest()
        # return pwd_context.verify(pwd, self.pwd)

    def to_dict(self):
        return json.loads(self.to_json())

    def clean(self):
        # self.pwd = hashlib.sha1(self.pwd).hexdigest()
        # Pre save hook to do custom cleaning
        pass

    def add_tag(self, tags):
        self.tags.extend(tags)
        self.tags = list(set(self.tags))
        self.save()

    def get_id(self):
        return unicode(self.session_token)

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def is_active(self):
        """True, as all users are active."""
        return self.is_account_verified()

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        self.last_token = s.dumps({'email':self.id})
        self.save()
        return self.last_token

    def clear_auth_token(self, expiration=600):
        self.last_token = ''
        self.save()

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None, -1 # valid token, but expired
        except BadSignature:
            return None, -2 # invalid token
        user = User.objects(email=data['email']).first()
        return user, 0


def setTestUserData():
    User.objects(email = "tom@kidocode.com").delete()
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    data = json.loads(open(cur_dir + '/users.json').read())
    tasks = json.loads(open(cur_dir + '/tasks.json').read())['tasks']
    status = ['backlog', 'todo', 'progress', 'done', 'delayed']
    tags = ['general', 'kportal', 'kadmin', 'gym', 'koffice', 'khello', 'kpeople']

    usr = User(**data['users'][0])
    usr.hash_pwd()
    usr.generate_session_token()
    usr.generate_active_account_token()
    myTags = []

    import random
    random.shuffle(tasks)
    for t in tasks[:30]:
        t['status'] = random.choice(status)
        t['tags'] = list(set([random.choice(tags), random.choice(tags)]))
        myTags += t['tags']
        task = Task(content=t['content'], status=t['status'], owner=usr.id, tags=t['tags'])
        task.duration_type = random.choice(['day', 'hour', 'month'])

        if task.duration_type == "hour":
            task.duration = random.randint(3, 10)
        elif task.duration_type == "day":
            task.duration = random.randint(1, 10)
        elif task.duration_type == "month":
            task.duration = random.randint(1, 12)

        task.calculate_hour_duration()
        task.time_created = time.time() - random.randint(0, int(task.duration_hour * 1.3)) * 3600
        task.calculate_left()
        task.delayed = task.left_hours <= 0
        for i in range(random.randint(0, 5)):
            task.add_note(tasks[i]['content'], False)
        task.save()

    usr.tags = list(set(myTags))
    usr.save()
    usr.verify_account(usr.account_active_token)

def setupUserData():
    import random
    #User.drop_collection()
    #Task.drop_collection()
    status = ['backlog', 'todo', 'progress', 'done', 'delayed']
    tags = ['general', 'kportal', 'kadmin', 'gym', 'koffice', 'khello', 'kpeople']
    if not User.objects().count():
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        data = json.loads(open( cur_dir + '/users.json').read())
        tasks = json.loads(open( cur_dir + '/tasks.json').read())['tasks']
        for u in data['users']:
            usr = User(**u)
            usr.hash_pwd()
            usr.generate_session_token()
            usr.generate_active_account_token()
            myTags = []

            if usr.id == 'unclecode@kidocode.com':
                usr.generate_welcome_tasks()
                pass
            else:
                random.shuffle(tasks)
                for t in tasks[:30]:
                    t['status'] = random.choice(status)
                    t['tags'] = list(set([random.choice(tags), random.choice(tags)]))
                    myTags += t['tags']
                    task = Task(content = t['content'], status = t['status'], owner = usr.id, tags = t['tags'])
                    task.duration_type = random.choice(['day', 'hour', 'month'])

                    if task.duration_type  == "hour":
                        task.duration = random.randint(3, 10)
                    elif task.duration_type  == "day":
                        task.duration = random.randint(1, 10)
                    elif task.duration_type  == "month":
                        task.duration = random.randint(1, 12)

                    task.calculate_hour_duration()
                    task.time_created = time.time() - random.randint(0, int(task.duration_hour * 1.3)) * 3600
                    task.calculate_left()
                    task.delayed = task.left_hours <= 0
                    for i in range(random.randint(0, 5)):
                        task.addNote(tasks[i]['content'], False)
                    task.save()

            usr.tags = list(set(myTags))
            usr.save()
            if usr.id == 'unclecode@kidocode.com':
                usr.verify_account(usr.account_active_token)

    tasks = json.loads(open(cur_dir + '/tasks.json').read())['tasks']
    uTasks = Task.objects(owner="unclecode@kidocode.com")
    for t in uTasks:
        for i in range(random.randint(0, 4)):
            t.addNote(tasks[i]['content'], False)
        t.save()

    print "Done"

