__author__ = 'unclecode'
# Import flask dependencies
from flask import Blueprint, render_template, abort, session, redirect, url_for
from flask_login import current_user
from app import mongodb

# Define the blueprint: 'XXX', set its url prefix: app.url/PREFIX
mod_index = Blueprint('index', __name__)


# Set the route and accepted methods
# @mod_index.route('/<page>')
# @mod_index.route('/', methods=['GET', 'POST'], defaults = {'page':'index'})
@mod_index.route('/')
def index():
    try:
        return redirect('/auth')
        #return render_template("index/index.html")
    except Exception as e:
        print(e)
        abort(404)

