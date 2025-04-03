from pydantic import BaseModel, Field, ConfigDict


class UserProfileSchema(BaseModel):
    """
    Schema for returning authenticated user profile.
    """

    sub: str = Field(..., description="User unique identifier (Auth0 sub).")
    name: str = Field(..., description="User full name.")
    email: str = Field(..., description="User email address.")

    model_config = ConfigDict(
    json_schema_extra={
        "example": {
            "sub": "auth0|abc123",
            "name": "John Doe",
            "email": "john@example.com"
        }
    }
)
