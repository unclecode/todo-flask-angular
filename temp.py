# import wsgiref
#
# def app(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/html')])
#     return [b'Hello, world!']
#
# if __name__ == '__main__':
#     try:
#         print __file__
#         from wsgiref.simple_server import make_server
#         httpd = make_server('', 8081, app)
#         print('Serving on port 8080...')
#         httpd.serve_forever()
#     except KeyboardInterrupt:
#         print('Goodbye.')


# from flask_httpauth import HTTPBasicAuth
#
# app = Flask(__name__)
# auth = HTTPBasicAuth()
#
# users = {
#     "john": "hello",
#     "susan": "bye"
# }
#
# @auth.get_password
# def get_pw(username):
#     if username in users:
#         return users.get(username)
#     return None
#
# @auth.error_handler
# def auth_error():
#     return redirect('/')
#
#
# @app.route('/member')
# @auth.login_required
# def member():
#     return "Hello, %s!" % auth.username()
#
#
import sys, os, json, hashlib, uuid, base64, random
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')
from flask import Flask, make_response, redirect, request, url_for, Response, current_app, g
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user, fresh_login_required, confirm_login
from flask_principal import Principal, Permission, RoleNeed, AnonymousIdentity, identity_changed, identity_loaded, Identity, UserNeed, ActionNeed, ItemNeed, TypeNeed

app = Flask(__name__)

app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

Principal(app)

# Roles or Needs
role_needs = { k : RoleNeed(k) for k in ['owner', 'viewer', 'editor', 'dev']}
role_actions = { k : ActionNeed(k) for k in ['insert', 'edit', 'delete', 'share', 'read']}

editor_permission = Permission(role_needs['editor'])
# editor_permission.needs = set([roles['editor']])
owner_permission = Permission(role_needs['owner'])
viewer_permission = Permission(role_needs['viewer'])
dev_permission = Permission(role_needs['dev'])

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"
login_manager.refresh_view = "/login"
login_manager.session_protection = "strong"

from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "des_crypt"],  pbkdf2_sha256__rounds = 29000) #argon2

from itsdangerous import URLSafeTimedSerializer, Signer, TimestampSigner
s = Signer('secret-key')
t = s.sign("hello")
print s.unsign(s)
s = URLSafeTimedSerializer('secret-key')
t = s.dumps({'s':23})
print s.loads(t, max_age=10)


class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = "123" # pwd_context.hash(self.name + self.password)
        self.session_token = hashlib.md5(self.name + self.password).hexdigest()
        self.session_token = pwd_context.using(salt_size=16).hash(self.name + self.password)
        self.email_active = True
        self.roles = [random.choice(role_needs.values())]
        self.item_needs = [ItemNeed("task", "delete", 1), ItemNeed("task", "delete", 2)]
        if id == 1:
            self.roles = [role_needs['viewer']]
            self.roles = [role_needs['editor'], role_needs['owner']]
            self.roles = [role_needs['owner'], role_needs['dev']]

    def update_token(self):
        self.session_token = pwd_context.using(salt_size=16).hash(self.name + self.password)

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

    def get_id(self):
        return self.session_token

    @property
    def is_active(self):
        return self.email_active



users = [User(id) for id in range(1, 21)]

def getUserByUsername(name):
    try:
        return [u for u in users if u.name == name][0]
    except:
        return None



@login_manager.user_loader
def load_user(session_token):
    # here is the place that I verify the given token, now becoz it's not dependency on password
    # so I can do lot's of thinks, for example may be token expiered! Or may be token is old, may be
    # account is inactivate and ... Working with token has these abilities
    # in my User model i must have a function verify_token to return the true false
    # I can use "g" to holder user! g.user = ...
    try:
        return [u for u in users if u.session_token == session_token][0]
    except:
        return None

@login_manager.request_loader
def load_user_from_request(request):
    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        # search in user dev database is there anyone with the given api key? then return user object whoch is an isntance of UserMixin
        return None

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            import base64
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        # search in user dev database is there anyone with the given api key? then return user object whoch is an isntance of UserMixin
        return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        u = getUserByUsername(username)
        if u and u.password == password:
            #user = load_user(u)
            res = login_user(u, remember=True)
            if res:
                identity_changed.send(current_app._get_current_object(), identity = Identity(u.get_id()))
                return redirect(request.args.get("next", '/member'))
            else:
                return "your account not activate, activate it here <a href ='/member/active/" + u.name + "'>activate</a>"
    return '''
            <form method="POST">
                Username: <input type="text" value = "user1" name="username"/><br/>
                Password: <input type="password" value = "123" name="password"/><br/>
                <input type="submit" value="Log in"/>
            </form>
        '''


# @app.before_request
# @login_required
# def before_request():
#     #this make all request to need login
#     pass

@app.route('/member')
@login_required
def member():
    #To fresh current session
    ## confirm_login()
    return """hello member <a href ='/member/em'>Change Email</a>. <a href ='/member/ch/124'>Change</a>. <a href ='/secure'>Secure</a>. <a href ='/logout'>Logout</a>.
    <hr>
    <ul>
        <ol><a href = "/member/view">View</a></ol>
        <ol><a href = "/member/view">Edit</a></ol>
        <ol><a href = "/member/view">Share</a></ol>
        <ol><a href = "/member/delete">Delete</a></ol>
    """
    pass

@app.route('/member/view')
@login_required
@viewer_permission.require(http_exception=403)
def m_view():
    return "viewer is required"
    pass

@app.route('/member/edit')
@login_required
@editor_permission.require(http_exception=403)
def m_edit():
    return 'editting'
    pass

@app.route('/member/share')
@login_required
@owner_permission.require()
@editor_permission.require(http_exception=403)
def m_share():
    return 'owner and editor'
    pass

@app.route('/member/delete')
@login_required
@owner_permission.require()
def m_delete():
    return "admin"
    pass

@app.route('/api/delete/<int:id>')
@login_required
@dev_permission.require()
def m_delete_id(id):
    p = Permission(ItemNeed("task", "delete", id))
    if p.can():
        return "you can delete " + str(id)
    else:
        return "you can't delete " + str(id)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.get_id()))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(role)

    if hasattr(current_user, 'item_needs'):
        for item in current_user.item_needs:
            identity.provides.add(item)


@app.route('/secure')
@fresh_login_required
def secure():
    return "You are in very secure fresh area! Even your session must be fresh! Like when you are at middle of a fucking bank page that if you loos your session it will ask you reathenticate!. <a href = '/member'>member</a>"
    pass


@app.route('/member/ch/<string:pwd>')
@login_required
def member_change_password(pwd):
    u = getUserByUsername(current_user.name)
    u.password = "124"
    u.update_token()
    return redirect('/member')
    pass

@app.route('/member/em')
@login_required
def member_change_email():
    u = getUserByUsername(current_user.name)
    u.email_active = False
    return redirect('/logout')
    pass

@app.route('/member/active/<name>')
def member_active(name):
    u = getUserByUsername(name)
    u.email_active= True
    return redirect('/member')
    pass

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')
    pass

@app.route('/')
def index():
    return 'hello index'

@app.errorhandler(403)
def not_found(error):
    missed_needs = list(error.description.needs)
    missed_needs = [(n.value, n.method) for n in missed_needs]
    return 'You have no access to here! You need ' + ', '.join([v + ' ' + m for v, m in missed_needs]), 403


if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 7070)
