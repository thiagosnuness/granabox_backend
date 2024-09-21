from datetime import date, datetime
import pytz

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# Set a fixed timezone for schema example generation
local_tz = pytz.timezone("America/Sao_Paulo")
local_time = datetime.now(local_tz)
utc_time = local_time.astimezone(pytz.utc)


class ItemSchema(BaseModel):
    """
    Schema for validating and representing an item in the system.

    Attributes:
        id (int): Unique identifier for each item, generated automatically.
        recurrence_id (str): Unique identifier for a series of recurring items.
        recurrence (Optional[str]): Recurrence of the item('Única', 'Mensal').
        months (Optional[int]): The number of recurring months to create.
        type (str): The type of the item ('A Pagar', 'Pago', 'Rendimentos').
        description (str): A brief description of the item.
        amount (float): The monetary value of the item. Must be greater than 0.
        due_date (date): The due date of the item in the format YYYY-MM-DD.
        due_status (str):The due status('VENCIDO', 'VENCE HOJE', 'A VENCER').
        transaction_date (datetime): The date and time when the item was
        created or last modified.
        label_id (int): The ID of the label associated with the item.
    """

    id: int = Field(
        ...,
        description=(
            "Unique identifier for each item, generated automatically."
        ),
    )
    recurrence_id: Optional[str] = Field(
        None, description="Unique identifier for a series of recurring items."
    )
    recurrence: Optional[str] = Field(
        "Única", description="Recurrence of the item ('Única' or 'Mensal')."
    )
    months: Optional[int] = Field(
        12,
        description=(
            "The number of recurring months to create (default is 12)."
        ),
    )
    type: str = Field(
        ...,
        description="The type of the item ('A Pagar', 'Pago', 'Rendimentos').",
    )
    description: str = Field(..., description="The description of the item.")
    amount: float = Field(..., gt=0, description="The amount of the item.")
    due_date: date = Field(
        ..., description="The due date of the item in format YYYY-MM-DD."
    )
    due_status: Optional[str] = Field(
        None,
        description="The due status ('VENCIDO', 'VENCE HOJE', 'A VENCER',etc)",
    )
    transaction_date: datetime = Field(
        ...,
        description="The date and time the item was created or last modified.",
    )
    label_id: int = Field(
        ..., description="The ID of the label associated with the item."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "recurrence_id": None,
                "recurrence": "Única",
                "months": None,
                "type": "A Pagar",
                "description": "Aluguel",
                "amount": 1500,
                "due_date": datetime.now(local_tz).strftime("%Y-%m-%d"),
                "due_status": "VENCE HOJE",
                "transaction_date": utc_time.strftime("%Y-%m-%d %H:%M:%S"),
                "label": "Habitação",
                "label_id": 1,
            }
        }
    )


class AddItemSchema(BaseModel):
    """
    Schema for adding a new financial item.

    Attributes:
        type (str): The type of the item ('A Pagar', 'Pago', 'Rendimentos').
        description (str): A brief description of the item.
        amount (float): The monetary value of the item. Must be greater than 0.
        due_date (date): The due date of the item in the format YYYY-MM-DD.
        label_id (int): The ID of the label associated with the item.
    """

    type: str = Field(
        ...,
        description="The type of the item ('A Pagar', 'Pago', 'Rendimentos).",
    )
    description: str = Field(..., description="The description of the item.")
    amount: float = Field(..., gt=0, description="The amount of the item.")
    due_date: date = Field(
        ..., description="The due date of the item in format YYYY-MM-DD."
    )
    label_id: int = Field(
        ..., description="The ID of the label associated with the item."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "A Pagar",
                "description": "Aluguel",
                "amount": 1500,
                "due_date": datetime.now(local_tz).strftime("%Y-%m-%d"),
                "label_id": 1,
            }
        }
    )


class GetItemByIDSchema(BaseModel):
    """
    Schema for searches a specific financial item by ID.

    Attributes:
        id (int): Unique identifier for each item.
    """

    id: int = Field(..., description="Unique identifier for each item.")

    model_config = ConfigDict(json_schema_extra={"example": {"id": 1}})


class GetItemByDateSchema(BaseModel):
    """
    Schema for searching items by filtering by specific year and month and
    optionally by type.

    Attributes:
        year (str): The year of the item.
        month (str): The month of the item.
        type (str): The type of the item ('A Pagar', 'Pago', 'Rendimentos').
    """

    year: str = Field(..., description="The year of the item.")
    month: str = Field(..., description="The month of the item.")
    type: Optional[str] = Field(
        None,
        description="The type of the item ('A Pagar', 'Pago', 'Rendimentos').",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "recurrence_id": None,
                "recurrence": "Única",
                "months": 12,
                "type": "A Pagar",
                "description": "Aluguel",
                "amount": 1500,
                "due_date": datetime.now(local_tz).strftime("%Y-%m-%d"),
                "due_status": "VENCE HOJE",
                "transaction_date": utc_time.strftime("%Y-%m-%d %H:%M:%S"),
                "label": "Habitação",
                "label_id": 1,
            }
        }
    )


class GetYearsSchema(BaseModel):
    """
    Schema for the response that lists the available years for items.

    Attributes:
        min_year (int): The earliest year for which items exist.
        max_year (int): The latest year for which items exist.
    """

    min_year: int = Field(
        ..., description="The earliest year for which items exist."
    )
    max_year: int = Field(
        ..., description="The latest year for which items exist."
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"min_year": 2022, "max_year": 2026}}
    )


class GetDashboardOverviewSchema(BaseModel):
    """
    Schema for provides a financial overview including total income,
    total expenses, and savings.

    Attributes:
        year (str): The year of the item.
        month (str): The month of the item.
        type (str): The type of the item ('A Pagar', 'Pago', 'Rendimentos').
    """

    year: str = Field(..., description="The year of the item.")
    month: str = Field(..., description="The month of the item.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"savings": 0, "total_expenses": 0, "total_income": 0}
        }
    )


class EditItemSchema(BaseModel):
    """
    Schema for editing an existing finance item.

    Attributes:
        id (int): Unique identifier for each item.
        type (Optional[str]): Type of the item('A Pagar','Pago','Rendimentos').
        description (Optional[str]): A brief description of the item.
        amount (Optional[float]): The monetary value of the item.
        due_date (Optional[date]): Due date of the item in format YYYY-MM-DD.
        label_id (Optional[int]): The ID of the label associated with the item.
    """

    id: int = Field(..., description="Unique identifier for each item.")
    type: Optional[str] = Field(
        None,
        description="The type of the item ('A Pagar', 'Pago', 'Rendimentos').",
    )
    description: Optional[str] = Field(
        None, description="The description of the item."
    )
    amount: Optional[float] = Field(
        None, gt=0, description="The amount of the item."
    )
    due_date: Optional[date] = Field(
        None, description="The due date of the item in format YYYY-MM-DD."
    )
    label_id: Optional[int] = Field(
        None, description="The ID of the label associated with the item."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "type": "Pago",
                "description": "Aluguel",
                "amount": 1500,
                "due_date": datetime.now(local_tz).strftime("%Y-%m-%d"),
                "label_id": 1,
            }
        }
    )


class EditItemStatusSchema(BaseModel):
    """
    Schema for Updates the status of an item (e.g. from 'A Pagar' to 'Pago').

    Attributes:
        id (int): Unique identifier for each item.
        type (str): The type of the item ('A Pagar', 'Pago').
    """

    id: int = Field(..., description="Unique identifier for each item.")
    type: str = Field(
        ..., description="The type of the item ('A Pagar', 'Pago')."
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"id": 1, "type": "Pago"}}
    )


class DeleteItemByIDSchema(BaseModel):
    """
    Schema for remove a specific item by ID.

    Attributes:
        id (int): Unique identifier for each item.
    """

    id: int = Field(..., description="Unique identifier for each item.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Item removed successfully"}
        }
    )
