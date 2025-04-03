import os

from flask_openapi3 import Tag
from flask import jsonify

from app import app
from api.schemas.auth_config_schema import *


auth_tag = Tag(
    name="Auth Configuration",
    description=(
        "Provides Auth0 configuration values required for frontend login."
        )
)


@app.get(
    "/auth-config",
    tags=[auth_tag],
    summary="Retrieve public Auth0 configuration",
    description=(
        "Returns the Auth0 domain, clientId, audience for frontend usage."
        ),
    responses={
        "200": {
            "description": "Auth0 configuration values retrieved successfully.",
            "content": {
                "application/json": {
                    "schema": AuthConfigSchema.model_json_schema()
                }
            },
        }
    },
)
def get_auth_config():
    """
    Retrieves public Auth0 configuration required for frontend initialization.

    These values are used by the frontend to initialize Auth0 authentication.

    Returns:
    - domain: Auth0 domain.
    - clientId: Public client ID for the SPA application.
    - audience: API audience configured in Auth0.
    """
    return jsonify({
        "domain": os.getenv("AUTH0_DOMAIN", ""),
        "clientId": os.getenv("AUTH0_CLIENT_ID", ""),
        "audience": os.getenv("AUTH0_AUDIENCE", ""),
    }), 200
