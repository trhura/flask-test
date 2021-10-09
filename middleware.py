import jwt

from flask import request, current_app
from functools import wraps

from jwt.exceptions import InvalidTokenError
from response import AuthorizationError, TokenValidationError

authorization_header = "Authorization"


def token_required(f):
    """Check for jwt token in header and validate the token"""

    @wraps(f)
    def validate_jwt_token(*args, **kwargs):
        token = None

        if authorization_header in request.headers:
            token = request.headers[authorization_header].split()[1]
        else:
            raise TokenValidationError("authorization token missing")

        try:
            request.claims = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
                options={
                    "require": ["exp", "sub"],
                    "verify_signature": True,
                    "verify_exp": True,
                },
            )
        except InvalidTokenError as ex:
            raise TokenValidationError(str(ex))

        return f(*args, **kwargs)

    return validate_jwt_token


def token_optional(f):
    """Check for jwt token in header and validate the token"""

    @wraps(f)
    def validate_jwt_token(*args, **kwargs):
        token = None

        if authorization_header in request.headers:
            token = request.headers[authorization_header].split()[1]

            try:
                request.claims = jwt.decode(
                    token,
                    current_app.config["SECRET_KEY"],
                    algorithms=["HS256"],
                    options={
                        "verify_signature": False,
                    },
                )
            except Exception:
                pass

        return f(*args, **kwargs)

    return validate_jwt_token


def admin_token_required(f):
    """Check for jwt token in header, validate the token and
    also check `adm` field in jwt token"""

    @wraps(f)
    def validate_jwt_token(*args, **kwargs):
        token = None

        if authorization_header in request.headers:
            token = request.headers[authorization_header].split()[1]
        else:
            raise TokenValidationError("authorization token missing")

        try:
            request.claims = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
                options={
                    "require": ["exp", "sub"],
                    "verify_signature": True,
                    "verify_exp": True,
                },
            )
        except InvalidTokenError as ex:
            raise TokenValidationError(str(ex))

        if not request.claims["adm"]:
            raise AuthorizationError("only admin user can access this route")

        return f(*args, **kwargs)

    return validate_jwt_token
