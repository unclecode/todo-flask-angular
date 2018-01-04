__author__ = 'unclecode'
import sys, os, json, hashlib, random
import mongoengine, re, time
from flask_login import UserMixin
from app import db
from calendar import monthrange
from bson.json_util import dumps

class Note(db.EmbeddedDocument):
    index = db.IntField()
    note = db.StringField()
    time_created = db.FloatField(default=time.time())
    time_updated = db.FloatField(default=time.time())

    def to_dict(self):
        res = json.loads(self.to_json())
        if '_id' in res:
            res['id'] = res['_id']['$oid']
            res.pop('_id', 0)
        return res

class Task(db.DynamicDocument, UserMixin):
    # fields arguments http://docs.mongoengine.org/guide/defining-documents.html#field-arguments
    owner = db.StringField(regex=re.compile(r'(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)', re.IGNORECASE))
    content = db.StringField(default=None)
    status = db.StringField(choices=['backlog', 'todo', 'progress', 'done', 'delayed'])
    tags = db.ListField(db.StringField())

    duration = db.FloatField(default= 24)
    duration_hour = db.FloatField(default= 24)
    left_hours = db.FloatField(default= 24)
    duration_type = db.StringField(default="day")

    delayed = db.BooleanField(default=False)
    removed = db.BooleanField(default=False)

    time_created = db.FloatField(default=time.time())
    time_updated = db.FloatField(default=time.time())
    type = db.StringField(default="task")
    notes = db.ListField(db.EmbeddedDocumentField(Note), default = [])



    meta = {
        'collection':'tasks',
        'indexes': [
            'email',
            'status',
            'tags',
            ('$content', '$notes.note')
        ],
        'ordering':['-time_updated', '+left_hours', '-notes.time_updated']
    }

    def calculate_hour_duration(self):
        if self.duration_type == "hour":
            self.duration_hour = self.duration
        elif self.duration_type == "day":
            self.duration_hour = self.duration * 24
        elif self.duration_type == "month":
            self.duration_hour = self.duration * 24 * 31
        pass

    def calculate_left(self):
        pad = 0
        if self.duration_type == "hour":
            pad = (1.0/60) * 5
        elif self.duration_type == "day":
            pad = 1
        elif self.duration_type == "month":
            pad = 1

        self.left_hours = int(pad + self.duration_hour - (time.time() - self.time_created) / 3600.00)
        pass

    @staticmethod
    def update_left_time():
        for task in Task.objects():
            task.calculate_left()
            task.save()
        pass

    def get_title(self):
        return ((self.content[:20] + '...') if len(self.content) > 20 else self.content).title()

    def add_note(self, note, save = True):
        n = Note()
        n.note = note
        n.time_updated = n.time_created = time.time()
        n.index = len(self.notes)
        self.notes = [n] + self.notes
        if save:
            self.save()
        return n

    def remove_note(self, index, save = True):
        self.notes = [n for n in self.notes if n.index != index]
        if save:
            self.save()

    def get_note_by_index(self, index):
        note = [n for n in self.notes if n.index == index]
        return note[0] if note else None

    def set_note_by_index(self, index, content, save = True):
        note = self.get_note_by_index(index)
        note.note = content
        note.time_updated = time.time()
        if save:
            self.save()

    def to_dict(self):
        res = json.loads(self.to_json())
        if '_id' in res:
            res['id'] = res['_id']['$oid']
            res.pop('_id', 0)
        return res


    def clean(self):
        # Pre save hook to do custom cleaning
        pass