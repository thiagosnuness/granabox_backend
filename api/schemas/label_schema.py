from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class LabelSchema(BaseModel):
    """
    Schema for validating and representing a label in the system.

    Attributes:
        id (int): Unique identifier for each label, generated automatically.
        name (str): The name of the label (e.g., 'Habitação', 'Saúde').
        is_default (bool): Indicates if the label is a default one or custom.
    """

    id: int = Field(
        ...,
        description=(
            "Unique identifier for each label, generated automatically."
        ),
    )
    name: str = Field(
        ..., description="The name of the label (e.g., 'Habitação', 'Saúde')."
    )
    is_default: bool = Field(
        False,
        description=(
            "Indicates if the label is a default one (True) or custom (False)."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id": 1, "name": "Habitação", "is_default": False}
        }
    )


class AddLabelSchema(BaseModel):
    """
    Schema for add a label in the system.

    Attributes:
        name (str): The name of the label (e.g., 'Habitação', 'Saúde').
        is_default (bool): Indicates if the label is a default one or custom.
    """

    name: str = Field(
        ..., description="The name of the label (e.g., 'Habitação', 'Saúde')."
    )
    is_default: bool = Field(
        False,
        description=(
            "Indicates if the label is a default one (True) or custom (False)."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "Habitação", "is_default": False}
        }
    )


class GetLabelByIDSchema(BaseModel):
    """
    Searches a specific label by ID.

    Attributes:
        id (int): Unique identifier for each item.
    """

    id: int = Field(..., description="Unique identifier for each label.")

    model_config = ConfigDict(json_schema_extra={"example": {"id": 1}})


class EditLabelSchema(BaseModel):
    """
    Schema for edit a label in the system.

    Attributes:
        name (str): The name of the label (e.g., 'Habitação', 'Saúde').
        is_default (bool): Indicates if the label is a default one or custom.
    """

    id: int = Field(..., description="Unique identifier for each label.")
    name: Optional[str] = Field(
        None,
        description="The name of the label (e.g., 'Habitação', 'Saúde').",
    )
    is_default: Optional[bool] = Field(
        False,
        description=(
            "Indicates if the label is a default one (True) or custom (False)."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id": 1, "name": "Habitação", "is_default": False}
        }
    )


class DeleteLabelByIDSchema(BaseModel):
    """
    Delete a specific label by ID.

    Attributes:
        id (int): Unique identifier for each item.
    """

    id: int = Field(..., description="Unique identifier for each label.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Label deleted successfully"}
        }
    )
