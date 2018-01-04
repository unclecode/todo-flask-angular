__author__ = 'unclecode'
import re, time
from flask_restful import fields

def email_validator(value, name):
   email = re.compile(r'(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)',re.IGNORECASE)
   if not email.match(value):
      raise ValueError("The parameter {} is not valid format. You passed {}.".format(name, value))
   return value


class ReadableTime(fields.Raw):
    def format(self, value):
        return [value, time.ctime(value)]