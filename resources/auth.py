from flask import redirect, url_for, session
from flask_smorest import Blueprint
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode

blp = Blueprint("Auth", "auth")

# auth0 implementation

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
    },server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration'
)

@blp.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("Auth.callback", _external=True)
    )

@blp.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return "Authorised"

@blp.route('/logout')
def logout():
    session.clear()
    params = {'client_id': '9D6AjN9xfEPsDiLT4Fc6MadIwDQXcCDI'}
    return redirect(oauth.auth0.api_base_url + '/v2/logout?' + urlencode(params))

# Function to check if a user is logged in using Auth0 authentication

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('Auth.login'))
        return f(*args, **kwargs)
    return decorated_function


    


