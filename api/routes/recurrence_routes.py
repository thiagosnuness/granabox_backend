from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
import uuid

from flask_openapi3 import Tag
from flask import jsonify, request

from app import app
from api import db
from api.models.item import Item
from api.models.label import Label
from api.schemas.recurrence_schema import *
from api.schemas.error_schema import ValidationErrorSchema
from api.utils.time_utils import get_user_timezone, calculate_due_status


recurrence_tag = Tag(
    name="Recurring Item Management",
    description=(
        "Operations related to managing recurring items, including creation, "
        "updating, and deletion."
    ),
)


@app.post(
    "/item/recurring",
    tags=[recurrence_tag],
    summary="Create recurring financial item",
    description=(
        "Creates a new recurring financial item with a specified frequency "
        "(e.g., monthly). The recurrence series is based on the initial due "
        "date and the number of months provided."
    ),
    responses={
        "201": {
            "description": "Recurring item created successfully.",
            "content": {
                "application/json": {
                    "schema": RecurringItemSchema.model_json_schema()
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
def add_recurring_item(form: AddRecurringItemSchema):
    """
    Adds a new recurring financial item to the database.

    This function creates a series of recurring financial items, starting
    from the initial due date. The recurrence frequency is determined
    by the number of months provided by the user.

    Parameters:
    - label_id: ID of the label to associate with the recurring items.
    - type: Type of the item (e.g., income, expense).
    - description: A brief description of the item.
    - amount: The monetary value of the item.
    - due_date: The start date for the recurrence (YYYY-MM-DD).
    - months: The number of months for which the item should recur.

    Returns:
    - A list of created recurring items with all their details.
    """
    # Fetch query parameters
    form = request.form

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
                    "msg": "Label not found.",
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
                        "msg": "Invalid date format. Expected YYYY-MM-DD.",
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
                        "Invalid due_date type. "
                        "Expected string or date object."
                    ),
                    "type_": "validation_error",
                }
            ),
            400,
        )

    start_date = due_date
    months_to_create = int(form.get("months")) or 12
    recurrence_id = str(uuid.uuid4())

    # Get user's timezone and convert transaction_date to UTC
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

    items = []
    for i in range(months_to_create, 0, -1):
        next_due_date = start_date + relativedelta(
            months=(months_to_create - i)
        )

        # Get the current local time and convert to UTC
        local_time = datetime.now(user_timezone)
        utc_time = local_time.astimezone(pytz.utc)

        type = form.get("type")

        new_item = Item(
            type=type,
            label=label,
            description=form.get("description"),
            amount=float(form.get("amount")),
            due_date=next_due_date,
            due_status=calculate_due_status(
                next_due_date, user_timezone, type
            ),
            recurrence="Mensal",
            months=i,
            recurrence_id=recurrence_id,
            transaction_date=utc_time,
        )
        db.session.add(new_item)
        items.append(new_item)

    db.session.commit()

    return jsonify([item.to_dict() for item in items]), 201


@app.get(
    "/item/recurring",
    tags=[recurrence_tag],
    summary="Retrieve recurring item by series ID",
    description=(
        "Searches for a recurring item by its recurrence ID, "
        "returning all items in the series."
    ),
    responses={
        "200": {
            "description": "Recurring items found",
            "content": {
                "application/json": {
                    "schema": RecurringItemSchema.model_json_schema()
                }
            },
        },
        "404": {
            "description": "No items found for this recurrence series",
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
def get_recurring_items_by_recurrence_id(query: GetRecurringItemByIDSchema):
    """
    Searches all items that belong to the same recurrence series
    by recurrence_id.

    Returns the item details if found, or an error if not.
    """
    # Fetch query parameters
    query = request.args
    recurrence_id = query.get("recurrence_id")

    recurring_items = Item.query.filter_by(recurrence_id=recurrence_id).all()

    if not recurring_items:
        return (
            jsonify(
                {
                    "loc": ["recurrence_id"],
                    "msg": "No items found for this recurrence series.",
                    "type_": "not_found_error",
                }
            ),
            404,
        )

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
                for item in recurring_items
            ]
        ),
        200,
    )


@app.put(
    "/item/recurring",
    tags=[recurrence_tag],
    summary="Edit recurring item",
    description=(
        "Edits a recurring item and updates future items in the series."
    ),
    responses={
        "200": {
            "description": "Recurring item updated",
            "content": {
                "application/json": {
                    "schema": EditRecurringItemSchema.model_json_schema()
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
        "404": {
            "description": "Item not found",
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
def edit_recurring_items(form: EditRecurringItemSchema):
    """
    Edits a recurring item and updates future items in the series.

    Updates the item's data, including the type, description, amount,
    due date, and recurrence.
    """
    # Fetch query parameters
    form = request.form

    # Fetch the item by ID from the query parameters (item_id is required)
    item_id = int(form.get("id"))
    item = Item.query.get(item_id)
    if not item:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "Item not found.",
                    "type_": "not_found_error",
                }
            ),
            404,
        )

    if not item.recurrence_id:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "This item is not part of a recurring series.",
                    "type_": "validation_error",
                }
            ),
            400,
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
                        "msg": "Label not found.",
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
            new_due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            return (
                jsonify(
                    {
                        "loc": ["due_date"],
                        "msg": "Invalid date format. Expected YYYY-MM-DD.",
                        "type_": "validation_error",
                    }
                ),
                400,
            )
    else:
        new_due_date = item.due_date

    # Update the optional fields if provided
    if form.get("type"):
        item.type = form.get("type")

    if form.get("description"):
        item.description = form.get("description")

    if form.get("amount"):
        try:
            item.amount = float(form.get("amount"))
        except (ValueError, TypeError):
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

    # Fetch the user's timezone and convert transaction_date to UTC
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

    # Update transaction date for the current item
    item.transaction_date = utc_time

    # Fetch and update future items in the recurrence series
    future_items = Item.query.filter(
        Item.recurrence_id == item.recurrence_id,
        Item.due_date >= item.due_date,
    ).all()

    for future_item in future_items:
        if item.label_id:
            future_item.label_id = item.label_id
        if item.type:
            future_item.type = item.type
        if item.description:
            future_item.description = item.description
        if item.amount:
            future_item.amount = item.amount
        # Recalculate the due date for future items based on the new due date
        future_item.due_date = new_due_date + relativedelta(
            months=(int(future_item.id) - item_id)
        )
        future_item.due_status = calculate_due_status(
            future_item.due_date, user_timezone, future_item.type
        )
        future_item.transaction_date = utc_time

    db.session.commit()

    return jsonify({"message": "Recurring items updated successfully"}), 200


@app.delete(
    "/item/recurring",
    tags=[recurrence_tag],
    summary="Delete recurring item",
    description="Removes a recurring item and future items in the series.",
    responses={
        "200": {
            "description": "Recurring items removed successfully.",
            "content": {
                "application/json": {
                    "schema": DeleteRecurringItemByIDSchema.model_json_schema()
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
def remove_recurring_items(query: DeleteRecurringItemByIDSchema):
    """
    Removes future recurring items based on the current item.

    Returns a success message if the item was removed.
    """
    # Fetch query parameters
    query = request.args
    # Fetch the item by ID from the query parameters (item_id is required)
    item_id = query.get("id")
    item = Item.query.get(item_id)
    if not item:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "Item not found.",
                    "type_": "not_found_error",
                }
            ),
            404,
        )

    if not item.recurrence_id:
        return (
            jsonify(
                {
                    "loc": ["id"],
                    "msg": "This item is not part of a recurring series.",
                    "type_": "validation_error",
                }
            ),
            400,
        )

    # Delete future recurring items
    future_items = Item.query.filter(
        Item.recurrence_id == item.recurrence_id,
        Item.due_date > item.due_date,
    ).all()

    for future_item in future_items:
        db.session.delete(future_item)

    # Fetch remaining items after deletion and update their 'months' field
    remaining_items = (
        Item.query.filter(
            Item.recurrence_id == item.recurrence_id,
            Item.due_date <= item.due_date,
        )
        .order_by(Item.due_date)
        .all()
    )

    # Update the 'months' field to reflect the new sequence
    for i, remaining_item in enumerate(remaining_items, start=1):
        remaining_item.months = len(remaining_items) - i + 1

    db.session.commit()
    return jsonify({"message": "Future recurring items deleted"}), 200
