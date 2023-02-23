from db import db

class ProjectModel(db.Model):
    __tablename__ = "Projects"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = True, nullable = False)
    client = db.Column(db.String, unique = True, nullable = False)

    Manager = db.relationship("ManagerModel", back_populates = "Project",cascade = "all,delete")


