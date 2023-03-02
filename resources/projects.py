from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import ProjectModel,UserModel
from schemas import ProjectSchema, ProjectUpdateSchema
from resources.users import login_required


blp = Blueprint("Projects", "projects")


@blp.route("/project/<string:project_id>")

class Project(MethodView):
    
    @blp.response(200, ProjectSchema)
    def get(self, project_id):
        project = ProjectModel.query.get_or_404(project_id)
        return project
    
    def delete(self, project_id):
        project = ProjectModel.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return {"message": "Project deleted"}, 200
    
    @blp.arguments(ProjectUpdateSchema)
    @blp.response(200, ProjectSchema)
    def put(self, project_data, project_id):
        project = ProjectModel.query.get([project_id])

        if project:
            project.name = project_data["name"]
            project.client = project_data["client"]
        else:
            project = ProjectModel(id=project_id, **project_data)

        db.session.add(project)
        db.session.commit()

        return project
    


    
@blp.route("/project")

class ProjectList(MethodView):
    
    @blp.response(200, ProjectSchema(many=True))
    @login_required
    def get(self):
        return ProjectModel.query.all()
        
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



    

