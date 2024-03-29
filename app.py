from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from blocklist import Blocklist
from resources.projects import blp as projectblueprint
from resources.managers import blp as managerblueprint
from resources.users import blp as userblueprint


from db import db

def create_app():
    app = Flask(__name__)

    #setting https self signed certificate

    app.config["ENV"] = "development"
    app.config["DEBUG"] = True
    app.config["FLASK_RUN_CERT"] = "adhoc"

    # app configurations

    app.config["API_TITLE"] = "Project Manager API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["JWT_SECRET_KEY"] = "vicky"

    app.secret_key="my secret key"

    #   Auth0 configs

    app.config['AUTH0_DOMAIN'] = 'dev-u1sb6wm0ovrzs1ii.us.auth0.com'
    app.config['AUTH0_CLIENT_ID'] = '9D6AjN9xfEPsDiLT4Fc6MadIwDQXcCDI'
    app.config['AUTH0_CLIENT_SECRET'] = 'SEAUBQJO-_n0wZWnwVbTAlbPAfAyeu8zMYMGEUsK0MgqTWtS3as7m8tZumsLYjzz'
    app.config['AUTH0_CALLBACK_URL'] = 'http://localhost:5000/callback'
    

    
    

    db.init_app(app)
    api = Api(app)
    

    with app.app_context():
        db.create_all()

    api.register_blueprint(projectblueprint)
    api.register_blueprint(managerblueprint)
    api.register_blueprint(userblueprint)

    return app    



