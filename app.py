from flask import Flask
from flask_smorest import Api
from resources.projects import blp as projectblueprint
from resources.managers import blp as managerblueprint
from resources.auth import blp as authblueprint
from resources.auth import oauth
from db import db 

def create_app():
    app = Flask(__name__)
    app.config["API_TITLE"] = "Project Manager API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://xrxhxzxo:4ki8lS1a1VOkCBj010-PDBucRvEtk8_z@mahmud.db.elephantsql.com/xrxhxzxo"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Improves performance
    app.config["PROPAGATE_EXCEPTIONS"] = True # propagate the exceptions to the web server
    app.secret_key="my secret key"

    db.init_app(app)
    api = Api(app)
    oauth.init_app(app)
    
    with app.app_context():
        db.create_all()

    api.register_blueprint(projectblueprint)
    api.register_blueprint(managerblueprint)
    api.register_blueprint(authblueprint)

    return app    



