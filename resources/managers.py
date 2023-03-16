from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import ManagerModel
from schemas import ManagerSchema, ManagerUpdateSchema
from flask_jwt_extended import jwt_required
from resources.auth import login_required

blp = Blueprint("Managers", "managers")

@blp.route("/manager/<string:manager_id>")

class Manager(MethodView):
    
    @blp.response(200, ManagerSchema)
    def get(self, manager_id):
        manager = ManagerModel.query.get_or_404(manager_id)
        return manager
    
    def delete(self, manager_id):
        manager = ManagerModel.query.get_or_404(manager_id)
        db.session.delete(manager)
        db.session.commit()
        return {"message": "Manager deleted"}
    
    @blp.arguments(ManagerUpdateSchema)
    @blp.response(200, ManagerSchema)
    def put(self, manager_data, manager_id):
        manager = ManagerModel.query.get(manager_id)

        if manager:
            manager.name = manager_data["name"]
        else:
            manager = ManagerModel(id=manager_id, **manager_data)

        db.session.add(manager)
        db.session.commit()

        return manager

@blp.route("/manager")
class ManagerList(MethodView):
    
    
    @blp.response(200, ManagerSchema(many=True))
    @login_required
    def get(self):
        return ManagerModel.query.all()
    
    
    @blp.arguments(ManagerSchema)
    @blp.response(201, ManagerSchema)
    def post(self, manager_data):
        manager = ManagerModel(**manager_data)

        try:
            db.session.add(manager)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Name exists")    
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the manager.")

        return manager_data
    
    def delete(self):
        managers = ManagerModel.query.all()
        for manager in managers:
            db.session.delete(manager)
        db.session.commit()
        return {"message": "All managers deleted"}, 200

    
    