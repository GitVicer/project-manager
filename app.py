from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST
from resources.projects import blp as projectblueprint
from resources.managers import blp as managerblueprint
from resources.users import blp as userblueprint

from db import db

def create_app():
    app = Flask(__name__)
    app.config["API_TITLE"] = "Project Manager API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    db.init_app(app)
    api = Api(app)
    app.config["JWT_SECRET_KEY"] = "vicky"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    

    
    with app.app_context():
        db.create_all()

    api.register_blueprint(projectblueprint)
    api.register_blueprint(managerblueprint)
    api.register_blueprint(userblueprint)

    return app    


