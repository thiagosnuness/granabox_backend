from datetime import datetime, date
from pytz import timezone

from flask_openapi3 import Tag
from flask import jsonify, request
import jwt

from app import app
from api import db
from api.models.item import Item
from api.models.label import Label
from api.schemas.item_schema import *
from api.schemas.error_schema import ValidationErrorSchema
from api.utils.time_utils import get_user_timezone, calculate_due_status


item_tag = Tag(
    name="Item Management",
    description=(
        "Operations related to item registration, editing, viewing, "
        "and deletion."
    ),
)


@app.post(
    "/item",
    tags=[item_tag],
    summary="Create a new financial item",
    description=(
        "Creates a new financial item in the database, including type, "
        "description, amount, due date, and associated label. The item can "
        "be a single or recurring entry."
    ),
    responses={
        "201": {
            "description": "Item created successfully.",
            "content": {
                "application/json": {"schema": ItemSchema.model_json_schema()}
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
def add_item(form: AddItemSchema):
    """
    Adds a new financial item to the database.

    This function creates an item with all required financial details,
    including type, description, amount, due date, and recurrence.
    It supports both single and recurring items.

    Parameters:
    - label_id: ID of the label to associate with the item.
    - type: Type of the item (e.g., income, expense).
    - description: A brief description of the item.
    - amount: The monetary value of the item.
    - due_date: The due date of the item (YYYY-MM-DD).
    - recurrence: 'Única' for one-time or 'Mensal' for recurring.

    Returns:
    - The created item with all its details.
    """
    # Fetch query parameters
    form = request.form
    
    # Extract user_id (sub) from token, fallback to 'public' via Swagger
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Check if all required parameters are present
    required_params = [
        "label_id",
        "type",
        "description",
        "amount",
        "due_date",
    ]
    for param in required_params:
        if not form.get(param):
            return (
                jsonify(
                    {
                        "loc": [param],
                        "msg": f"Missing required parameter: {param}",
                        "type_": "validation_error",
                    }
                ),
                400,
            )

    # Fetch the label by ID
    label_id = form.get("label_id")
    label = Label.query.get(label_id)
    if not label:
        return (
            jsonify(
                {
                    "loc": ["label_id"],
                    "msg": "Label not found",
                    "type_": "not_found_error",
                }
            ),
            404,
        )

    # Check if query.due_date is a string, and convert it to a date object
    if isinstance(form.get("due_date"), str):
        try:
            due_date = datetime.strptime(
                form.get("due_date"), "%Y-%m-%d"
            ).date()
        except ValueError:
            return (
                jsonify(
                    {
                        "loc": ["due_date"],
                        "msg": "Invalid date format. Expected YYYY-MM-DD",
                        "type_": "validation_error",
                    }
                ),
                400,
            )
    elif isinstance(form.get("due_date"), date):
        due_date = form.get("due_date")
    else:
        return (
            jsonify(
                {
                    "loc": ["due_date"],
                    "msg": (
                        "Invalid due_date type. Expected string or date object"
                    ),
                    "type_": "validation_error",
                }
            ),
            400,
        )

    # Validate if the recurrence value is valid
    recurrence_value = form.get("recurrence", "Única")
    if recurrence_value not in ["Única", "Mensal"]:
        return (
            jsonify(
                {
                    "loc": ["recurrence"],
                    "msg": (
                        f"Invalid recurrence value: {recurrence_value}. "
                        f"Expected 'Única' or 'Mensal'"
                    ),
                    "type_": "validation_error",
                }
            ),
            400,
        )

    # Store transaction date in UTC
    user_timezone = get_user_timezone()
    if not user_timezone:
        return (
            jsonify(
                {
                    "loc": ["TimeZone"],
                    "msg": "Invalid time zone",
                    "type_": "validation_error",
                }
            ),
            400,
        )

    local_time = datetime.now(user_timezone)
    utc_time = local_time.astimezone(pytz.utc)

    type = form.get("type")

    new_item = Item(
        type=type,
        label=label,
        description=form.get("description"),
        amount=float(form.get("amount")),
        due_date=due_date,
        due_status=calculate_due_status(due_date, user_timezone, type),
        recurrence=recurrence_value,
        transaction_date=utc_time,
        user_id=user_id  # Injected from token or fallback
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201


@app.get(
    "/items",
    tags=[item_tag],
    summary="List all items",
    description="Searches all registered financial items.",
    responses={
        "200": {
            "description": "List of items",
            "content": {
                "application/json": {"schema": ItemSchema.model_json_schema()}
            },
        }
    },
)
def get_items():
    """
    Searches all registered financial items.

    Returns a complete list of items, including the details of each item.
    Filters the items by the user_id (Auth0 sub) extracted from the JWT token.
    If no token is provided (e.g., via Swagger), defaults to 'public'.
    """
    # Extract user_id (sub) from the token or fallback to 'public' for Swagger
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Query only items that belong to the authenticated user
    items = Item.query.filter_by(user_id=user_id).all()

    # Fetch the user's timezone using pytz
    user_timezone = request.headers.get("TimeZone", "UTC")
    user_tz = timezone(user_timezone)

    return (
        jsonify(
            [
                {
                    **item.to_dict(),
                    "transaction_date": item.transaction_date.replace(
                        tzinfo=timezone("UTC")
                    )
                    .astimezone(user_tz)
                    .strftime("%Y-%m-%d %H:%M:%S"),
                }
                for item in items
            ]
        ),
        200,
    )


@app.get(
    "/item",
    tags=[item_tag],
    summary="Retrieve item by ID",
    description="Searches for a specific financial item by ID.",
    responses={
        "200": {
            "description": "Item details",
            "content": {
                "application/json": {"schema": ItemSchema.model_json_schema()}
            },
        },
        "404": {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "403": {
            "description": "Access denied. Item does not belong to the user.",
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
def get_item(query: GetItemByIDSchema):
    """
    Searches for a specific financial item by ID.

    Returns the item details if found, or an error if not.
    The item must belong to the user identified by the token.
    """
    # Fetch query parameters
    query = request.args

    # Extract user_id (sub) from the token or fallback to 'public' for Swagger
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Fetch the item by ID from the query parameters (item_id is required)
    item_id = query.get("id")
    item = Item.query.get(item_id)
    if not item:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "Item not found",
                    "type_": "not_found_error",
                }
            ),
            404,
        )
    
    # Ensure the item belongs to the authenticated user
    if item.user_id != user_id:
        return (
            jsonify(
                {
                    "loc": ["user_id"],
                    "msg": "Unauthorized to access this item",
                    "type_": "access_denied",
                }
            ),
            403,
        )

    # Fetch the user's timezone using pytz
    user_timezone = request.headers.get("TimeZone", "UTC")
    user_tz = timezone(user_timezone)

    # Force conversion of transaction_date to the user's timezone
    local_time = item.transaction_date.replace(
        tzinfo=timezone("UTC")
    ).astimezone(user_tz)

    # Format the local time for the response
    formatted_local_time = local_time.strftime("%Y-%m-%d %H:%M:%S")

    return (
        jsonify(
            {
                **item.to_dict(),
                "transaction_date": formatted_local_time,
            }
        ),
        200,
    )


@app.get(
    "/items/date",
    tags=[item_tag],
    summary="List items by year and month",
    description=(
        "Searches for items filtered by year, month, and optionally by type."
    ),
    responses={
        "200": {
            "description": "List of items by date",
            "content": {
                "application/json": {
                    "schema": GetItemByDateSchema.model_json_schema()
                }
            },
        },
        "400": {
            "description": "Year and month are required",
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
def get_items_by_date(query: GetItemByDateSchema):
    """
    Searches for items filtered by specific year and month, and optionally
    by type.

    Returns a list of items filtered by year and month. If type is provided,
    also filters by type. Items are also filtered by user_id extracted
    from the JWT token, or 'public' when tested via Swagger.
    """
    # Fetch query parameters
    query = request.args

    year = query.get("year")
    month = query.get("month")
    item_type = query.get("type")

    if not year or not month:
        return (
            jsonify(
                {
                    "loc": ["year", "month"],
                    "msg": "Year and month are required",
                    "type_": "validation_error",
                }
            ),
            400,
        )
    
    # Extract user_id (sub) from the token or fallback to 'public' for Swagger
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Build query filtering by due date and user_id
    query = Item.query.filter(
        db.extract("year", Item.due_date) == year,
        db.extract("month", Item.due_date) == month,
        Item.user_id == user_id  # Filter items belonging to the user
    )

    if item_type:
        query = query.filter(Item.type == item_type)

    filtered_items = query.all()

    # Fetch the user's timezone using pytz
    user_timezone = request.headers.get("TimeZone", "UTC")
    user_tz = timezone(user_timezone)

    return (
        jsonify(
            [
                {
                    **item.to_dict(),
                    "transaction_date": item.transaction_date.replace(
                        tzinfo=timezone("UTC")
                    )
                    .astimezone(user_tz)
                    .strftime("%Y-%m-%d %H:%M:%S"),
                }
                for item in filtered_items
            ]
        ),
        200,
    )


@app.get(
    "/items/years",
    tags=[item_tag],
    summary="List available years for items",
    description="Returns the earliest and latest years for which items exist.",
    responses={
        "200": {
            "description": "Available years retrieved successfully",
            "content": {
                "application/json": {
                    "schema": GetYearsSchema.model_json_schema()
                }
            },
        },
        "404": {
            "description": "No items found.",
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
def get_years():
    """
    Fetch the earliest and latest years for which items exist.

    Returns the minimum and maximum years based on the `due_date` item.
    Only considers items that belong to the authenticated user.
    If there is no item, it defaults to the current year.
    """
    # Extract user_id (sub) from the token or fallback to 'public' for Swagger
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Query to get the minimum and maximum due date for the user's items
    min_date = (
        db.session.query(db.func.min(Item.due_date))
        .filter(Item.user_id == user_id)
        .scalar()
    )
    max_date = (
        db.session.query(db.func.max(Item.due_date))
        .filter(Item.user_id == user_id)
        .scalar()
    )

    # Get the current year for fallback
    current_year = datetime.now().year

    # If no items exist, return the current year
    if not min_date or not max_date:
        return (
            jsonify({"min_year": current_year, "max_year": current_year}),
            200,
        )

    # Extract the year from the min and max dates
    min_year = min_date.year
    max_year = max_date.year

    return (
        jsonify({"min_year": int(min_year), "max_year": int(max_year)}),
        200,
    )


@app.get(
    "/items/overview",
    tags=[item_tag],
    summary="Financial Overview",
    description=(
        "Provides a financial overview with total income, expenses, "
        "and savings."
    ),
    responses={
        "200": {
            "description": "Financial overview",
            "content": {
                "application/json": {
                    "schema": GetDashboardOverviewSchema.model_json_schema()
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
def get_dashboard_overview(query: GetDashboardOverviewSchema):
    """
    Provides a financial overview including total income, total expenses,
    and savings.

    Returns the total income, expenses, and the final balance.
    Filters results by user_id (Auth0 sub) extracted from the JWT token.
    Defaults to 'public' when tested via Swagger.
    """
    # Fetch query parameters
    query = request.args

    year = query.get("year")
    month = query.get("month")

    # Extract user_id (sub) from the token or fallback to 'public' for Swagger
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"
    
    # Calculate total income (type = 'Rendimentos') for the user
    total_income = (
        db.session.query(db.func.sum(Item.amount))
        .filter(
            Item.type == "Rendimentos",
            db.extract("month", Item.due_date) == month,
            db.extract("year", Item.due_date) == year,
            Item.user_id == user_id
        )
        .scalar()
        or 0
    )

    # Calculate total expenses (type = 'Pago') for the user
    total_expenses = (
        db.session.query(db.func.sum(Item.amount))
        .filter(
            Item.type == "Pago",
            db.extract("month", Item.due_date) == month,
            db.extract("year", Item.due_date) == year,
            Item.user_id == user_id
        )
        .scalar()
        or 0
    )

    savings = total_income - total_expenses

    return (
        jsonify(
            {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "savings": savings,
            }
        ),
        200,
    )


@app.put(
    "/item",
    tags=[item_tag],
    summary="Edit financial item",
    description=(
        "Edits an existing financial item, updating fields like type, "
        "description, amount, due date, and recurrence."
    ),
    responses={
        "200": {
            "description": "Item updated",
            "content": {
                "application/json": {"schema": ItemSchema.model_json_schema()}
            },
        },
        "404": {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "403": {
            "description": "Access denied. Item does not belong to the user.",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
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
def edit_item(form: EditItemSchema):
    """
    Edits an existing financial item.

    Updates the item's data, including the type, description, amount,
    due date, and recurrence. Only allows editing items that belong
    to the authenticated user.
    """
    # Fetch query parameters
    form = request.form

    # Extract user_id (sub) from the token or fallback to 'public' for Swagger
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Fetch the item by ID from the query parameters (item_id is required)
    item_id = form.get("id")
    item = Item.query.get(item_id)
    if not item:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "Item not found",
                    "type_": "not_found_error",
                }
            ),
            404,
        )
    
    # Ensure the item belongs to the authenticated user
    if item.user_id != user_id:
        return (
            jsonify(
                {
                    "loc": ["user_id"],
                    "msg": "Unauthorized to edit this item",
                    "type_": "access_denied",
                }
            ),
            403,
        )

    # Fetch the label by ID if provided
    label_id = form.get("label_id")
    if label_id:
        label = Label.query.get(label_id)
        if not label:
            return (
                jsonify(
                    {
                        "loc": ["label_id"],
                        "msg": "Label not found",
                        "type_": "not_found_error",
                    }
                ),
                404,
            )

        item.label = label

    # Check and parse the due_date if provided
    due_date_str = form.get("due_date")
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            item.due_date = due_date
        except ValueError:
            return (
                jsonify(
                    {
                        "loc": ["due_date"],
                        "msg": "Invalid date format. Expected YYYY-MM-DD",
                        "type_": "validation_error",
                    }
                ),
                400,
            )
    else:
        due_date = item.due_date
    # Validate and update the recurrence value if provided
    recurrence_value = form.get("recurrence")
    if recurrence_value and recurrence_value not in ["Única", "Mensal"]:
        return (
            jsonify(
                {
                    "loc": ["recurrence"],
                    "msg": (
                        f"Invalid recurrence value: {recurrence_value}."
                        f"Expected 'Única' or 'Mensal'"
                    ),
                    "type_": "validation_error",
                }
            ),
            400,
        )
    elif recurrence_value:
        item.recurrence = recurrence_value

    # Update the optional fields if provided
    if form.get("type"):
        item.type = form.get("type")

    if form.get("description"):
        item.description = form.get("description")

    if form.get("amount"):
        try:
            item.amount = float(form.get("amount"))
        except ValueError:
            return (
                jsonify(
                    {
                        "loc": ["amount"],
                        "msg": "Invalid amount. Must be a number.",
                        "type_": "validation_error",
                    }
                ),
                400,
            )
    # Store transaction date in UTC
    user_timezone = get_user_timezone()
    if not user_timezone:
        return (
            jsonify(
                {
                    "loc": ["TimeZone"],
                    "msg": "Invalid time zone",
                    "type_": "validation_error",
                }
            ),
            400,
        )

    local_time = datetime.now(user_timezone)
    utc_time = local_time.astimezone(pytz.utc)
    item.transaction_date = utc_time

    due_status = calculate_due_status(due_date, user_timezone, item.type)
    item.due_status = due_status

    db.session.commit()

    return jsonify(item.to_dict()), 200


@app.put(
    "/item/status",
    tags=[item_tag],
    summary="Edit item status",
    description="Edit the status of an item (e.g., from 'A Pagar' to 'Pago').",
    responses={
        "200": {
            "description": "Item status updated",
            "content": {
                "application/json": {"schema": ItemSchema.model_json_schema()}
            },
        },
        "404": {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "403": {
            "description": "Access denied. Item does not belong to the user.",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
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
def edit_item_status(form: EditItemStatusSchema):
    """
    Edits the status of an item (e.g. from 'A Pagar' to 'Pago').

    Returns the updated item data, or an error if the item is not found,
    if it does not belong to the user, or if there is a validation error.
    """
    # Fetch query parameters
    form = request.form

    # Extract user_id (sub) from the token or fallback to 'public' for Swagger
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Fetch the item by ID from the query parameters (item_id is required)
    item_id = form.get("id")
    item = Item.query.get(item_id)
    if not item:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "Item not found",
                    "type_": "not_found_error",
                }
            ),
            404,
        )

    # Ensure the item belongs to the authenticated user
    if item.user_id != user_id:
        return (
            jsonify(
                {
                    "loc": ["user_id"],
                    "msg": "Unauthorized to edit this item",
                    "type_": "access_denied",
                }
            ),
            403,
        )
    
    item.type = form.get("type")

    # Store transaction date in UTC
    user_timezone = get_user_timezone()
    if not user_timezone:
        return (
            jsonify(
                {
                    "loc": ["TimeZone"],
                    "msg": "Invalid time zone",
                    "type_": "validation_error",
                }
            ),
            400,
        )

    local_time = datetime.now(user_timezone)
    utc_time = local_time.astimezone(pytz.utc)
    item.transaction_date = utc_time

    due_status = calculate_due_status(item.due_date, user_timezone, item.type)
    item.due_status = due_status

    db.session.commit()

    return jsonify(item.to_dict()), 200


@app.delete(
    "/item",
    tags=[item_tag],
    summary="Delete financial item",
    description="Removes a specific financial item by ID.",
    responses={
        "200": {
            "description": "Item successfully removed.",
            "content": {
                "application/json": {
                    "schema": DeleteItemByIDSchema.model_json_schema()
                }
            },
        },
        "404": {
            "description": "Item not found",
            "content": {
                "application/json": {
                    "schema": ValidationErrorSchema.model_json_schema()
                }
            },
        },
        "403": {
            "description": "Access denied. Item does not belong to the user.",
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
def delete_item(query: DeleteItemByIDSchema):
    """
    Removes a specific financial item by ID.

    Returns a success message if the item was removed.
    Only allows deletion if the item belongs to the authenticated user.
    """
    # Fetch query parameters
    query = request.args

    # Extract user_id (sub) from the token or fallback to 'public' for Swagger
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get("sub", "public")
    except Exception:
        user_id = "public"

    # Fetch the item by ID from the query parameters (item_id is required)
    item_id = query.get("id")
    item = Item.query.get(item_id)
    if not item:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "Item not found",
                    "type_": "not_found_error",
                }
            ),
            404,
        )
    
    # Ensure the item belongs to the authenticated user
    if item.user_id != user_id:
        return (
            jsonify(
                {
                    "loc": ["user_id"],
                    "msg": "Unauthorized to delete this item",
                    "type_": "access_denied",
                }
            ),
            403,
        )

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Item removed successfully"}), 200
