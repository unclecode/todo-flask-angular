__author__ = 'unclecode'

# Easy managing CSRF
# http://flask-seasurf.readthedocs.io/en/latest/


import sys, os, json, hashlib, uuid, base64, random
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')
from flask import Flask, make_response, redirect, request, url_for, Response, current_app, g, jsonify, views, render_template_string, session
from flask_session import Session
from flask_seasurf import SeaSurf

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = "WOWOWOWOW"
Session().init_app(app)

# Avoid genereting token, then token will be Null in testing app
# app.config['TESTING'] = True
# app.config['CSRF_COOKIE_NAME']
# app.config['CSRF_COOKIE_TIMEOUT']
# app.config['CSRF_DISABLE']

csrf = SeaSurf(app)
# Validation will now be active for all requests whose methods are not GET, HEAD, OPTIONS, or TRACE.
# automatically it will ass _csrf_token to cookie


html = """
<form method="POST">
    <input type="text" name="usr" value="unclecode">
    <input type="password" name="pwd" value="123">
    <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
    <input type="submit" value="Submit">
</form>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    # assert request.form['_csrf_token'] == session['_csrf_token']
    if request.method == 'GET':
        return render_template_string(html)
    else:
        if request.form['usr'] == "unclecode" and request.form['pwd'] == "123":
            return "welcome"

@csrf.exempt
@app.route('/2', methods=['GET', 'POST'])
def index2():
    # try to chane _csrf_token in browser and submit form you will see its working
    # assert request.form['_csrf_token'] == session['_csrf_token']
    if request.method == 'GET':
        return render_template_string(html)
    else:
        if request.form['usr'] == "unclecode" and request.form['pwd'] == "123":
            return "welcome"


@csrf.include
@app.route('/3')
def index3():
    # assert request.cookies['_csrf_token'] == session['_csrf_token']
    return render_template_string("""hi {{ csrf_token() }}""")


@app.errorhandler(403)
def not_found(error):
    # record and block user account
    return make_response(
            jsonify(error=error.description)
            , 403
    )


if __name__ == "__main__":
    app.run(debug=True)
