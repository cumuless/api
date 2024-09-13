from marshmallow import Schema, fields, validate, ValidationError
from flask import request, jsonify, g
from functools import wraps
from marshmallow import ValidationError

class EmbedTextSchema(Schema):
    text = fields.Str(required=True, validate=validate.Length(min=1))

class NewUserSchema(Schema):
    userId = fields.Str(required=True)
    email = fields.Str(required=True)

class GetFromUserObjectSchema(Schema):
    userId = fields.Str(required=True)

class UserAndSourceSchema(Schema):
    userId = fields.Str(required=True)
    sourceId = fields.Str(required=True)

class UserAndQuerySchema(Schema):
    userId = fields.Str(required=True)
    query = fields.Str(required=True)

def validate_schema(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get request body
                request_data = request.get_json(silent=True) or {}
                
                # Get query parameters
                param_data = request.args.to_dict()

                # Combine both dictionaries
                combined_data = {**param_data, **request_data}

                # Validate combined data
                validated_data = schema().load(combined_data)

                # Pass the validated data to the view function via `g`
                g.validated_data = validated_data
            except ValidationError as err:
                return jsonify(err.messages), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator