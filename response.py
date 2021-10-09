from jsonschema import ValidationError
from werkzeug.exceptions import HTTPException
from flask import make_response, jsonify


def success_json(**kwargs):
    """Add a success field in jsonify response"""
    return jsonify(dict({"success": True}, **kwargs))


class UserNotFound(HTTPException):
    """Raise if the user does not exist and never existed."""

    code = 404
    description = "The request user is not found in our system"


class AuthenticationFailure(HTTPException):
    """Raise during login when the authentication fails"""

    code = 401
    description = "Failed to authenticate user"


class AuthorizationError(HTTPException):
    """Raise on accessing unauthorized resource"""

    code = 401
    description = "you do not have authorization to accesss this resource"


class TokenValidationError(HTTPException):
    """Raise during jwt token validation errors"""

    code = 401
    description = "missing or malformed jwt token"


def handle_http_exception(e):
    """Return JSON instead of text for HTTP errors."""

    message = e.description

    # use concise message for ValidationErrors
    if isinstance(e.description, ValidationError):
        message = e.description.message

    return make_response(
        jsonify(
            {
                "success": False,
                "message": message,
            }
        ),
        e.code,
    )
