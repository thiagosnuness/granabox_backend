from flask_openapi3 import Tag
from flask import jsonify, request
import jwt

from app import app
from api import db
from api.models.label import Label
from api.schemas.label_schema import *
from api.schemas.error_schema import ValidationErrorSchema


label_tag = Tag(
    name="Label Management",
    description=(
        "Operations related to label registration, editing, viewing, "
        "and deletion."
    ),
)


@app.post(
    "/label",
    tags=[label_tag],
    summary="Create a new custom label",
    description=(
        "Creates a new custom label for financial items. The label can "
        "be marked as default or non-default."
    ),
    responses={
        "201": {
            "description": "Label created successfully.",
            "content": {
                "application/json": {
                    "schema": LabelSchema.model_json_schema()
                }
            },
        },
        "400": {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "422": {
            "description": "Unprocessable Entity",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
    },
)
def add_label(form: AddLabelSchema):
    """
    Creates a new custom label in the database.

    This function allows the user to create a label that can be used to
    categorize financial items. The label can be either default or custom.

    Parameters:
    - name: The name of the label.
    - is_default: Indicates whether the label is a default option (true/false).

    Returns:
    - The created label with its details.
    """
    # Fetch query parameters
    form = request.form

    # Extract user_id from token (or fallback to 'public' and default label)
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Validate and convert 'is_default' value
    is_default_value = form.get("is_default", "false").lower()
    if is_default_value in ["true"]:
        is_default = True
        user_id = "public"
    elif is_default_value in ["false"]:
        is_default = False
    else:
        return (
            jsonify(
                {
                    "loc": ["is_default"],
                    "msg": (
                        "Invalid value for is_default. "
                        "Expected 'true', 'false'."
                    ),
                    "type_": "validation_error",
                }
            ),
            400,
        )

    # Check if a label with the same name already exists
    name = form.get("name")
    existing_label = Label.query.filter_by(name=name).first()
    if existing_label:
        return (
            jsonify(
                {
                    "loc": ["name"],
                    "msg": f"Label with name '{name}' already exists.",
                    "type_": "validation_error",
                }
            ),
            400,
        )

    # Create the new label, linking it to the authenticated user
    new_label = Label(
        name=form.get("name"),
        is_default=is_default,
        user_id=user_id
    )
    db.session.add(new_label)
    db.session.commit()
    return jsonify(new_label.to_dict()), 201


@app.get(
    "/labels",
    tags=[label_tag],
    summary="List all labels",
    description="Retrieves all labels (default and custom) from the database.",
    responses={
        "200": {
            "description": "List of labels",
            "content": {
                "application/json": {
                    "schema": LabelSchema.model_json_schema()
                }
            },
        }
    },
)
def get_labels():
    """
    Retrieves all labels (default and custom) from the database.

    Returns only the labels that belong to the current user,
    or are publicly available ('public').
    """
    # Extract user_id from token (or fallback to 'public' and default label)
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Query labels that belong to the current user or are public
    labels = Label.query.filter(Label.user_id.in_([user_id, "public"])).all()

    return jsonify([label.to_dict() for label in labels]), 200


@app.get(
    "/label",
    tags=[label_tag],
    summary="Retrieve label by ID",
    description="Searches a specific label by its ID.",
    responses={
        "200": {
            "description": "Label details",
            "content": {
                "application/json": {
                    "schema": LabelSchema.model_json_schema()
                }
            },
        },
        "404": {
            "description": "Label not found",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "403": {
            "description": "Access denied. Label does not belong to the user.",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "422": {
            "description": "Unprocessable Entity",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
    },
)
def get_label(query: GetLabelByIDSchema):
    """
    Retrieve a specific label by ID.

    Returns the label details if found and belongs to the authenticated user,
    or an error if not found or unauthorized.
    """
    # Fetch query parameters
    query = request.args

    # Extract user_id from token (or fallback to 'public' and default label)
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Fetch the label by ID from the query parameters (label_id is required)
    label_id = query.get("id")
    label = Label.query.get(label_id)
    if not label:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "Label not found.",
                    "type_": "not_found_error",
                }
            ),
            404,
        )

    # Restrict access if label does not belong to the user or isn't public
    if label.user_id not in [user_id, "public"]:
        return (
            jsonify(
                {
                    "loc": ["user_id"],
                    "msg": "Access denied. Label does not belong to the user.",
                    "type_": "access_denied",
                }
            ),
            403,
        )
    
    return jsonify(label.to_dict()), 200


@app.put(
    "/label",
    tags=[label_tag],
    summary="Update label by ID",
    description="Updates a specific label by its ID.",
    responses={
        "200": {
            "description": "Label updated",
            "content": {
                "application/json": {
                    "schema": LabelSchema.model_json_schema()
                }
            },
        },
        "400": {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "403": {
            "description": "Access denied. Label does not belong to the user.",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "404": {
            "description": "Label not found",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "422": {
            "description": "Unprocessable Entity",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
    },
)
def edit_label(form: EditLabelSchema):
    """
    Updates a specific label by ID.

    Updates the label's data, including the name and is_default.

    Parameters:
    - name: The new name for the label.
    - is_default: Updates whether the label is a default label (true/false).

    Returns:
    - The updated label with its details.
    """
    # Fetch query parameters
    form = request.form

    # Extract user_id from token (or fallback to 'public' and default label)
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Fetch the label by ID from the query parameters (label_id is required)
    label_id = form.get("id")
    label = Label.query.get(label_id)
    if not label:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "Label not found.",
                    "type_": "not_found_error",
                }
            ),
            404,
        )
    
    # Restrict access if label does not belong to the user or isn't public
    if label.user_id not in [user_id, "public"]:
        return (
            jsonify(
                {
                    "loc": ["user_id"],
                    "msg": "Access denied. Label does not belong to the user.",
                    "type_": "access_denied",
                }
            ),
            403,
        )

    # Update the optional fields if provided
    if form.get("is_default"):
        # Validate and convert 'is_default' value
        is_default_value = form.get("is_default", "false").lower()
        if is_default_value in ["true"]:
            is_default = True
            label.is_default = is_default
            user_id = "public"
        elif is_default_value in ["false"]:
            is_default = False
            label.is_default = is_default
        else:
            return (
                jsonify(
                    {
                        "loc": ["is_default"],
                        "msg": (
                            "Invalid value for is_default. "
                            "Expected 'true', 'false'."
                        ),
                        "type_": "validation_error",
                    }
                ),
                400,
            )

    if form.get("name"):
        # Check if a label with the same name already exists
        name = form.get("name")
        existing_label = Label.query.filter(
            Label.name == name, Label.id != label_id
        ).first()
        if existing_label:
            return (
                jsonify(
                    {
                        "loc": ["name"],
                        "msg": f"Label with name '{name}' already exists.",
                        "type_": "validation_error",
                    }
                ),
                400,
            )
        else:
            label.name = name

    db.session.commit()
    return jsonify(label.to_dict()), 200


@app.delete(
    "/label",
    tags=[label_tag],
    summary="Delete label",
    description="Removes a specific label by ID.",
    responses={
        "200": {
            "description": "Label deleted successfully.",
            "content": {
                "application/json": {
                    "schema": DeleteLabelByIDSchema.model_json_schema()
                }
            },
        },
        "403": {
            "description": "Access denied. Label does not belong to the user.",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "404": {
            "description": "Label not found",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "422": {
            "description": "Unprocessable Entity",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
    },
)
def delete_label(query: DeleteLabelByIDSchema):
    """
    Deletes a label by ID.

    Returns a success message if the label was removed.
    Access is restricted to the owner of the label or public labels.
    """
    # Fetch query parameters
    query = request.args

    # Extract user_id from token (or fallback to 'public' and default label)
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"


    # Fetch the label by ID from the query parameters (label_id is required)
    label_id = query.get("id")
    label = Label.query.get(label_id)
    if not label:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "Label not found.",
                    "type_": "not_found_error",
                }
            ),
            404,
        )
    
    # Restrict deletion if label does not belong to the user or isn't public
    if label.user_id not in [user_id, "public"]:
        return (
            jsonify(
                {
                    "loc": ["user_id"],
                    "msg": "Access denied. Label does not belong to the user.",
                    "type_": "access_denied",
                }
            ),
            403,
        )

    db.session.delete(label)
    db.session.commit()
    return jsonify({"message": "Label deleted successfully"}), 200
