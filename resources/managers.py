from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import ManagerModel
from schemas import ManagerSchema

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
    
# implement put operation

@blp.route("/manager")
class ManagerList(MethodView):
    
    @blp.response(200, ManagerSchema(many=True))
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

        return manager