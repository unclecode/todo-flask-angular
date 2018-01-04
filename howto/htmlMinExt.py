__author__ = 'unclecode'

# HTMLMIN Extension
# https://github.com/hamidfzm/Flask-HTMLmin

import sys, os, json, hashlib, uuid, base64, random
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')
from flask import Flask, make_response, redirect, request, url_for, Response, current_app, g, jsonify, views, render_template_string, session
from flask_htmlmin import HTMLMIN

app = Flask(__name__)
app.config['DEBUG'] = False

# To switch the minification
app.config['MINIFY_PAGE'] = not app.config['DEBUG']
HTMLMIN(app)

@app.route('/')
def index():
    return render_template_string(
        """
<form method="POST">
    <input type="text" name="usr" value="unclecode">
    <input type="password" name="pwd" value="123">



    <input type="hidden" name="_csrf_token" value="dsd">
    <input type="submit" value="Submit">
</form>
""")

if __name__ == "__main__":
    app.run()
