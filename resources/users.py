from flask.views import MethodView
from flask import redirect, url_for, request, session, jsonify
from google_auth_oauthlib.flow import Flow
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required
)
from passlib.hash import pbkdf2_sha256
from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST
from authlib.integrations.flask_client import OAuth
from functools import wraps
from urllib.parse import urlencode


# auth0

AUTH0_CLIENT_ID = '9D6AjN9xfEPsDiLT4Fc6MadIwDQXcCDI'
AUTH0_CLIENT_SECRET = 'SEAUBQJO-_n0wZWnwVbTAlbPAfAyeu8zMYMGEUsK0MgqTWtS3as7m8tZumsLYjzz'
AUTH0_DOMAIN = 'dev-u1sb6wm0ovrzs1ii.us.auth0.com'
AUTH0_CALLBACK_URL = 'http://localhost:5000/callback'

oauth = OAuth()

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url='https://{domain}'.format(domain=AUTH0_DOMAIN),
    access_token_url='https://{domain}/oauth/token'.format(domain=AUTH0_DOMAIN),
    authorize_url='https://{domain}/authorize'.format(domain=AUTH0_DOMAIN),
    client_kwargs={
        'scope': 'openid profile email',
    },
)

blp = Blueprint("Users", "users")

@blp.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)

@blp.route('/callback')
def callback():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    # Store user info in session or database
    return "You are now authorised to access the data"

@blp.route('/logout')
def logout():
    session.clear()
    params = {'client_id': '9D6AjN9xfEPsDiLT4Fc6MadIwDQXcCDI'}
    return redirect(oauth.auth0.api_base_url + '/v2/logout?' + urlencode(params))



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



# Function to check if a user is logged in using google authentication

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            return redirect(url_for('Users.login'))
        return f(*args, **kwargs)
    return decorated_function

# end

    

@blp.route('/logout')
def logout():
    session.pop('google_token', None)
    return "Logged out"

# Implementation of google authentication ends
