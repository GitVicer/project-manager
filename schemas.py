from marshmallow import Schema, fields, validate

class PlainProjectSchema(Schema):
    id = fields.Int(dump_only = True)
    name = fields.Str(required=True,validate=validate.Length(min=1,max=20))
    client =  fields.Str(required=True,validate=validate.Length(min=1,max=20))

class PlainManagerSchema(Schema):
    id = fields.Int(dump_only = True)
    name = fields.Str(required=True,validate=validate.Length(min=1,max=20))
  
class ProjectSchema(PlainProjectSchema):
    managers = fields.List(fields.Nested(PlainManagerSchema()),dump_only = True) 

class ManagerSchema(PlainManagerSchema):
    project_id = fields.Int(required = True,load_only = True) 
    project = fields.Nested(PlainProjectSchema(),dump_only=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    AdminStatus = fields.Bool()

class ManagerUpdateSchema(Schema):
    name = fields.Str(required = True,validate=validate.Length(min=1,max=20))   

class ProjectUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1,max=20))  
    client = fields.Str(validate=validate.Length(min=1,max=20))