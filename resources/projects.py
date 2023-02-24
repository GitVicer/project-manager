from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import ProjectModel
from schemas import ProjectSchema

blp = Blueprint("Projects", "projects")


@blp.route("/project/<string:project_id>")
class Project(MethodView):
    
    @jwt_required()
    @blp.response(200, ProjectSchema)
    def get(self, project_id):
        project = ProjectModel.query.get_or_404(project_id)
        return project
    
    @jwt_required()
    def delete(self, project_id):
        project = ProjectModel.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return {"message": "Project deleted"}, 200
    
@blp.route("/project")
class ProjectList(MethodView):
    
    @jwt_required()
    @blp.response(200, ProjectSchema(many=True))
    def get(self):
        return ProjectModel.query.all()
    
    @jwt_required()
    @blp.arguments(ProjectSchema)
    @blp.response(201, ProjectSchema)
    def post(self, project_data):
        project = ProjectModel(**project_data)
        try:
            db.session.add(project)
            db.session.commit()
        except IntegrityError:
            abort(400, message = "A project or client with that name already exists")
        except SQLAlchemyError:
            abort(500, message = "An error occured while entering the data")
        return project_data   



    

