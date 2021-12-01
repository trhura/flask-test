import jwt

from flask import request, current_app
from functools import wraps

from jwt.exceptions import InvalidTokenError
from response import TokenValidationError

from models import User

authorization_header = "Authorization"


def auth_token_required(f):
    """Check for jwt token in header and validate the token"""

    @wraps(f)
    def validate_jwt_token(*args, **kwargs):
        token = None

        if authorization_header in request.headers:
            token = request.headers[authorization_header].split()[1]
        else:
            raise TokenValidationError("authorization token missing")

        try:
            claims = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
                options={
                    "require": ["exp", "sub"],
                    "verify_signature": True,
                    "verify_exp": True,
                },
            )

            request.user_id = claims["sub"]
            request.admin_user = claims["adm"]

        except InvalidTokenError as ex:
            raise TokenValidationError(str(ex))

        user = User.query.filter_by(uuid=request.user_id).first()
        if not user:
            raise TokenValidationError("the authenticated user is no longer valid")

        return f(*args, **kwargs)

    return validate_jwt_token


def auth_token_optional(f):
    """Check for the optional jwt token in header without validation"""

    @wraps(f)
    def validate_jwt_token(*args, **kwargs):
        token = None

        if authorization_header in request.headers:
            token = request.headers[authorization_header].split()[1]

            try:
                claims = jwt.decode(
                    token,
                    current_app.config["SECRET_KEY"],
                    algorithms=["HS256"],
                    options={
                        "verify_signature": False,
                    },
                )

                request.user_id = claims["sub"]
                request.admin_user = claims["adm"]

                user = User.query.filter_by(uuid=request.user_id).first()
                if not user:
                    raise TokenValidationError(
                        "the authenticated user is no longer valid"
                    )

            except Exception:
                pass

        return f(*args, **kwargs)

    return validate_jwt_token
