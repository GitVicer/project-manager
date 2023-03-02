from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required
)
from passlib.hash import pbkdf2_sha256
from flask import redirect, url_for, session, request
from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST
from flask_oauthlib.client import OAuth
from functools import wraps

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
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200

# Implementation of google authentication

oauth = OAuth()

google = oauth.remote_app(
    'google',
    consumer_key='300154338446-vgfljlou2df9rd4k4m52shvpk0i0kd99.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token'
)

# Function to check if a user is logged in using google authentication

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            return redirect(url_for('Users.login'))
        return f(*args, **kwargs)
    return decorated_function

# end

@blp.route("/login")
def login():
    return google.authorize(callback=url_for('Users.authorized', _external=True))

@blp.route('/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    return "you are now authorized to operate"
    
@google.tokengetter
def get_google_token():
    return session.get('google_token')

@blp.route('/logout')
def logout():
    session.pop('google_token', None)
    return "Logged out"

# Implementation of google authentication ends