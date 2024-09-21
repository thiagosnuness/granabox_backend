from flask_openapi3 import Tag
from flask import redirect

from app import app


home_tag = Tag(
    name="Home",
    description="Redirect to OpenAPI documentation",
    doc_ui=False,
)


@app.get(
    "/",
    tags=[home_tag],
    summary="Redirect to OpenAPI documentation",
    description=(
        "This route redirects the user to the OpenAPI documentation page."
    ),
    responses=(
        {"302": {"description": "Redirects to the OpenAPI documentation"}}
    ),
    doc_ui=False,
)
def home():
    """
    Redirects to /openapi, a screen that allows you to choose the documentation
    style.
    """
    return redirect("/openapi")
