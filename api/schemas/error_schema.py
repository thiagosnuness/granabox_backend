from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ValidationErrorSchema(BaseModel):
    """
    Schema for validation errors.

    Attributes:
        ctx (Optional[dict]): Additional context for the error, optional.
        loc (List[str]): The location of the error (e.g., field name).
        msg (str): A computer-readable message describing the error.
        type_ (str): A human-readable explanation of the error.
    """

    ctx: Optional[dict] = Field(
        None,
        description=(
            "Context providing additional information about the error."
        ),
    )
    loc: List[str] = Field(
        ..., description="The location of the error (e.g., field name)."
    )
    msg: str = Field(
        ..., description="A computer-readable message describing the error."
    )
    type_: str = Field(
        ..., description="A human-readable explanation of the error."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ctx": None,
                "loc": ["field_name"],
                "msg": "This field is required.",
                "type_": "validation_error",
            }
        }
    )
