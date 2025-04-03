from flask_openapi3 import Tag
from flask import jsonify, request
import jwt

from app import app
from api.schemas.user_schema import *
from api.schemas.error_schema import ValidationErrorSchema


user_tag = Tag(
    name="User",
    description="Operations related to authenticated user information."
)


@app.get(
    "/me",
    tags=[user_tag],
    summary="Get authenticated user info",
    description="Returns the user's name, email, and sub (user_id).",
    responses={
        "200": {
            "description": "User profile information",
            "content": {
                "application/json": {
                    "schema": UserProfileSchema.model_json_schema()
                }
            },
        },
        "401": {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
    },
)
def get_authenticated_user():
    """
    Returns basic information about the authenticated user.

    Extracts name, email, and sub from the provided Authorization token.
    This endpoint is useful for displaying user information in the frontend.
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        namespace = "http://127.0.0.1"
        user_info = {
            "sub": decoded_token.get("sub"),
            "name": decoded_token.get(f"{namespace}/name"),
            "email": decoded_token.get(f"{namespace}/email"),
        }
        return jsonify(user_info), 200
    except Exception:
        return (
            jsonify(
                {
                    "loc": ["Authorization"],
                    "msg": "Invalid or missing access token.",
                    "type_": "unauthorized",
                }
            ),
            401,
        )