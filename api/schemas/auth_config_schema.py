from pydantic import BaseModel, Field, ConfigDict


class AuthConfigSchema(BaseModel):
    """
    Schema for returning public Auth0 configuration used by the frontend.

    Attributes:
        domain (str): Auth0 domain used for authentication.
        clientId (str): Auth0 public client ID.
        audience (str): Auth0 audience configured for API access.
    """

    domain: str = Field(
        ..., description="Auth0 domain used for authentication."
    )
    clientId: str = Field(..., description="Auth0 public client ID.")
    audience: str = Field(
        ..., description="Auth0 audience configured for API access."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "domain": "your-domain.auth0.com",
                "clientId": "YOUR_CLIENT_ID",
                "audience": "https://your-domain.auth0.com/api/v2/"
            }
        }
    )
