__author__ = 'unclecode'

# GRavatar Extiension
# https://pypi.python.org/pypi/Flask-Gravatar

import sys, os, json, hashlib, uuid, base64, random
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')
from flask import Flask, make_response, redirect, request, url_for, Response, current_app, g, jsonify, views, render_template_string, session
from flask_gravatar import Gravatar

app = Flask(__name__)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    use_ssl=False,
                    base_url=None)

@app.route('/')
def index():
    return render_template_string("""<img src = "{{ 'zzz.sochi@gmail.com' | gravatar }}" alt="gr"/>""")

@app.route('/2')
def index2():
    return render_template_string("""<img src = "{{ 'zzz.sosssschi@gmail.com' | gravatar(size=200, rating='x') }}" alt="gr"/>""")


if __name__ == "__main__":
    app.run(debug=True)
