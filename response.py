from jsonschema import ValidationError
from werkzeug.exceptions import HTTPException
from flask import make_response, jsonify


def success_json(**kwargs):
    """Add a success field in jsonify response"""
    return jsonify(dict({"success": True}, **kwargs))


def http_exception_handler(e):
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


class DatabaseError(HTTPException):
    """Raise during errrors on database queries, update etc"""

    code = 500
    description = "Internal database error occured"


class ExistingUserError(HTTPException):
    """Raise while adding user when there is an existing username"""

    code = 400
    description = "The username is already being used in the system"


class TimezoneNotFound(HTTPException):
    """Raise when relevant timezone record is not found"""

    code = 404
    description = "unable to find specified timezone"


class InvalidTimezoneError(HTTPException):
    """Raise when creating timezone with wrong tzname"""

    code = 400
    description = "The given timezone is not valid"
