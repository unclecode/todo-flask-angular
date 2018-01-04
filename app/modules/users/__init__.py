__author__ = 'unclecode'
# Import flask dependencies
from flask import Blueprint, render_template, abort, session, redirect, url_for
from flask_login import login_required
from app import mongodb

mod_users = Blueprint('users', __name__, template_folder= "views", static_folder= "static" )


# Set the route and accepted methods
# @mod_index.route('/<page>')
# @mod_index.route('/', methods=['GET', 'POST'], defaults = {'page':'index'})
@mod_users.route('/')
@login_required
def index():
    try:
        return render_template("users.index.html", page_ctrl = "userCtrl as vm")
    except Exception as e:
        print(e)
        abort(404)

