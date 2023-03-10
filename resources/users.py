from flask.views import MethodView
from flask import redirect, url_for, session, request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_jwt,
    jwt_required
)
from passlib.hash import pbkdf2_sha256
from flask import redirect, url_for
from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import Blocklist
from flask_oauthlib.client import OAuth

import requests

blp = Blueprint("Users", "users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")
        
        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )

        db.session.add(user)
        db.session.commit()

        if user.id==1:
            user.AdminStatus = True

        db.session.commit()

        return {"message": "User created successfully."}, 201



@blp.route("/user/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
    
    @jwt_required()
    def put(self, user_id):
        current_user_id = get_jwt_identity()
        current_user = UserModel.query.get_or_404(current_user_id)
        if current_user.AdminStatus == True:
            user = UserModel.query.get_or_404(user_id)
            if user.AdminStatus == False:
                user.AdminStatus = True
                db.session.commit()
                name = user.username
                return{"message" : f"{name} is now an admin"}
            else:
                user.AdminStatus = False    
                db.session.commit()
                name = user.username
                return{"message" : f"{name} is not an admin now"}
        else:
            abort(400, message="Admin privilege required")

    
@blp.route("/user")

class ProjectList(MethodView):
    
    @blp.response(200, UserSchema(many=True))
    def get(self):
        return UserModel.query.all()

@blp.route("/refresh")

class TokenRefresh(MethodView):
    
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()["jti"]
        Blocklist.add(jti)
        return {"access_token": new_token}, 200
    
#Implementation of auth0

auth0_domain = 'dev-u1sb6wm0ovrzs1ii.us.auth0.com'
client_id = '9D6AjN9xfEPsDiLT4Fc6MadIwDQXcCDI'
client_secret = 'SEAUBQJO-_n0wZWnwVbTAlbPAfAyeu8zMYMGEUsK0MgqTWtS3as7m8tZumsLYjzz'
callback_url = 'https://localhost:5000/callback'
    
# checking decorator

def requires_auth(f):
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated



 
# Login route
@blp.route('/login')
def login():
    return auth0.authorize(callback=url_for('Users.auth0_callback', _external=True))

# Define callback route
@blp.route('/auth0_callback')
def auth0_callback():
    resp = auth0.authorized_response()
    session['auth0_token'] = resp['access_token']
    return "you are authorized"

# Define logout route
@blp.route('/logout')
def logout():
    session.clear()
    return 'logged out'


# Function to check admin status

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            return redirect(url_for('Users.login'))
        google_token = session["google_token"]
        headers = {"Authorization": f"Bearer {google_token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers)
        user_email = response.json()["email"]

        if user_email not in ["vickydwivedi989@gmail.com"]:
            return
        else:
            return f(*args, **kwargs)
        
    return decorated_function

# Function to check if a user is logged in using auth0 authentication

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'profile' not in session:
            return redirect(url_for('Users.login'))
        return f(*args, **kwargs)
    return decorated_function

# end
oauth = OAuth()

auth0 = oauth.remote_app(
    'auth0',
    consumer_key='9D6AjN9xfEPsDiLT4Fc6MadIwDQXcCDI',
    consumer_secret='SEAUBQJO-_n0wZWnwVbTAlbPAfAyeu8zMYMGEUsK0MgqTWtS3as7m8tZumsLYjzz',
    base_url='dev-u1sb6wm0ovrzs1ii.us.auth0.com',
    access_token_url='dev-u1sb6wm0ovrzs1ii.us.auth0.com/oauth/token',
    authorize_url='dev-u1sb6wm0ovrzs1ii.us.auth0.com/authorize',
    request_token_params={
        'scope': 'openid profile email'
    },
)

@blp.route('/authorized')
def authorized():
    resp = google.authorized_response()
    session['google_token'] = (resp['access_token'])
    if "profile" in session:
        google_token = session["google_token"]
        headers = {"Authorization": f"Bearer {google_token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)
        user_info = response.json()
        user_email = user_info["email"]
    if user_email in ["vickydwivedi989@gmail.com"]:
        return "you are admin, authorized to operate"
    else:    
        return "you are now authorized to operate but restircted to limited info"
    


