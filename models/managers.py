from db import db

class ManagerModel(db.Model):
    __tablename__ = "Managers"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = True, nullable = False)

    project_id = db.Column(db.Integer, db.ForeignKey("Projects.id"), unique = False, nullable = False)
    project = db.relationship("ProjectModel", back_populates= "managers")