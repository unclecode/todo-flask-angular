__author__ = 'unclecode'

from app import basicAuth, tokenAuth
from flask import Blueprint, render_template, abort, session, redirect, request, g, jsonify, render_template_string
from flask_login import login_user, logout_user, login_required, current_user
from flask_restful import reqparse
from app.models.user import User
from app.models.validators import email_validator
from app import app, login_manager, mail
from flask_mail import Message

mod_auth = Blueprint('auth', __name__, template_folder="views", static_folder="static")

login_parser = reqparse.RequestParser(bundle_errors=True)
login_parser.add_argument('email', type=email_validator, required=True)
login_parser.add_argument('pwd', type=str, required=True)
login_parser.add_argument('remember', type=bool, choices=[True, False], default=False)


# This uses to remind user credential for "Remember Me" in flask-login
@login_manager.user_loader
def load_user(session_token):
    return User.objects(session_token=session_token).first()

@mod_auth.route('/')
def index():
    # show login page
    if current_user and current_user.is_authenticated():
        return redirect('/users')
    return render_template("auth.index.html")
    pass

@mod_auth.route('/request_verification/<email>')
def request_verify(email):
    user = User.objects(email=email).first()
    if user and not user.is_account_verified():
        email = "unclecode@kidocode.com"
        #html="""<div>Click <a href="{0}auth/verify/{1}/{2}" target="_blank">here</a></div>""".format(app.config['SERVER_ADDRESS'], email, user.account_active_token),
        msg = Message(
            html=render_template("auth.verify_email.html").format(app.config['SERVER_ADDRESS'], email, user.account_active_token),
            subject="DidIt Assistant, Please Verify Your Account",
            recipients=[email])
        mail.send(msg)
        return jsonify({'results':True})
    return jsonify({'results':False, 'msg':'Account already verified'}), 400

@mod_auth.route('/verify/<email>/<token>')
def verify(email, token):
    user = User.objects(email=email).first()
    if user:
        res = user.verify_account(token)
        return redirect('/auth?email={email}&v='.format(email=email) + ('1' if res else '0'))
    return redirect('/auth?email={email}/v=0'.format(email=email))
    #return jsonify({'results':res, 'msg': 'Account already verified' if res else ''}), 100 if res else 400

@mod_auth.route('/me')
def me():
    if current_user:
        return jsonify({'result':True, 'me': current_user.getMe()})
    # show login page
    return jsonify({'result':False}), 400
    pass



@mod_auth.route('/login', methods=['GET', 'POST'])
def login():
    # first a simple login based on username and pwd
    # then use flask-login to login the user with login_user
    if current_user and current_user.is_authenticated():
        current_user.clear_auth_token()
        logout_user()
        return jsonify({'result': False, 'code':-1, "msg":"Duplicate login detected!"}), 400

    args = login_parser.parse_args()
    user = User.objects(email=args['email']).first()
    if not user or not user.verify_pwd(args['pwd']):
        return jsonify({'result':False, 'code':-1, 'msg':"Login failed! Wrong username, password."}), 400

    user.authenticated = True
    user.save()
    login_user(user, args['remember'])
    return jsonify({'result':True})


# to request api token, and must be called after standard login
@mod_auth.route('/token')
@mod_auth.route('/token/<int:expiration>')
@login_required
def get_api_token(expiration = 100 * 60 * 60):
    token = current_user.generate_auth_token(expiration)
    return jsonify({'token': token, 'expiration':expiration*1000})

# in header we need Authorization which is "token TOKEN_VALUE" first parameter is authorization type
# All token-based request must have header Authorization as "token TOKEN_VALUE"
@mod_auth.route('/token_need')
@tokenAuth.login_required
def token_need():
    return "toke is okay access is ok"

# it will be used to check the given token, while we have tokenAuth.login_required
@tokenAuth.verify_token
def verify_token(token):
    user, status = User.verify_auth_token(token)
    if not user:
        return False
    g.user = user
    return True

@mod_auth.route('/logout')
@login_required
def logout():
    current_user.authenticated = False
    current_user.save()
    logout_user()
    session.clear()
    return jsonify({'result':True})

@mod_auth.route('/logout2')
@login_required
def logout2():
    current_user.authenticated = False
    current_user.save()
    logout_user()
    session.clear()
    return redirect('/')


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return 'unauthorized'

# @mod_auth.route('/settings')
# @login_required
# def settings():
#     return "yes with login"
#     pass

# @basicAuth.verify_password
# def verify_pwd(email, pwd):
#     # temporarly
#     return True
#     user = User.objects(email=email).first()
#     if not user or user.verify_pwd(pwd):
#         return False
#     g.user = user
#     return True
