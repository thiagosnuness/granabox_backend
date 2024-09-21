from datetime import date, datetime
import pytz
import uuid

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# Set a fixed timezone for schema example generation
local_tz = pytz.timezone("America/Sao_Paulo")
local_time = datetime.now(local_tz)
utc_time = local_time.astimezone(pytz.utc)


class RecurringItemSchema(BaseModel):
    """
    Schema for validating and representing recurring items in the system.

    Attributes:
        id (int): Unique identifier for each item, generated automatically.
        recurrence_id (str): Unique identifier for a series of recurring items.
        recurrence (Optional[str]): Recurrence of the item('Única', 'Mensal').
        months (Optional[int]): The number of recurring months to create.
        type (str): The type of the item ('A Pagar', 'Pago', 'Rendimentos').
        description (str): A brief description of the item.
        amount (float): The monetary value of the item.
        due_date (date): The starting due date in YYYY-MM-DD format.
        due_status (str):The due status('VENCIDO', 'VENCE HOJE', 'A VENCER').
        transaction_date (datetime): The date and time when the item was
        created or last modified.
        label_id (int): The ID of the label for the recurring item.
    """

    id: Optional[int] = Field(
        None,
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
    description: str = Field(
        ..., description="A brief description of the item."
    )
    amount: float = Field(
        ..., gt=0, description="The monetary value of the item."
    )
    due_date: date = Field(
        ..., description="The starting due date in YYYY-MM-DD format."
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
        ..., description="The ID of the label for the item."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "recurrence_id": str(uuid.uuid4()),
                "recurrence": "Mensal",
                "months": 12,
                "type": "A Pagar",
                "description": "Conta de Luz",
                "amount": 500,
                "due_date": datetime.now(local_tz).strftime("%Y-%m-%d"),
                "due_status": "VENCE HOJE",
                "transaction_date": utc_time.strftime("%Y-%m-%d %H:%M:%S"),
                "label": "Habitação",
                "label_id": 1,
            }
        }
    )


class AddRecurringItemSchema(BaseModel):
    """
    Schema for adding a new recurring item.

    Attributes:
        recurrence (Optional[str]): Recurrence of the item('Única', 'Mensal').
        months (Optional[int]): The number of recurring months to create.
        type (str): The type of the item ('A Pagar', 'Pago', 'Rendimentos').
        description (str): A brief description of the item.
        amount (float): The monetary value of the item.
        due_date (date): The due date of the item in the format YYYY-MM-DD.
        label_id (int): The ID of the label associated with the item.
    """

    months: Optional[int] = Field(
        12,
        description=(
            "The number of recurring months to create (default is 12)."
        ),
    )
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
                "months": 12,
                "type": "A Pagar",
                "description": "Aluguel",
                "amount": 1500,
                "due_date": datetime.now(local_tz).strftime("%Y-%m-%d"),
                "label_id": 1,
            }
        }
    )


class GetRecurringItemByIDSchema(BaseModel):
    """
    Schema for searches a specific recurring items by ID.

    Attributes:
        recurrence_id (str): Unique identifier for a series of recurring items.
    """

    recurrence_id: str = Field(
        ..., description="Unique identifier for a series of recurring items."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recurrence_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class EditRecurringItemSchema(BaseModel):
    """
    Schema for editing an existing recurring item.

    Attributes:
        id (int): Unique identifier for each item.
        type (Optional[str]):Type of the item('A Pagar', 'Pago', 'Rendimentos')
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
            "example": {"message": "Recurring items updated successfully"}
        }
    )


class DeleteRecurringItemByIDSchema(BaseModel):
    """
    Schema for remove a specific recurring item by ID.

    Attributes:
        id (int): Unique identifier for each item.
    """

    id: int = Field(..., description="Unique identifier for each item.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Future recurring items deleted"}
        }
    )
