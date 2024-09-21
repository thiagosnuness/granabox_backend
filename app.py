import os

from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS

from api import db
from api.schemas.error_schema import ValidationErrorSchema
from error_handlers import register_error_handlers


# Swagger Configuration
info = Info(
    title="Granabox API",
    version="1.0.0",
    description=(
        "API for financial management of items, labels and recurrences."
    ),
)

app = OpenAPI(
    __name__, info=info, validation_error_model=ValidationErrorSchema
)

# Register the error handlers with the Flask app
register_error_handlers(app)

# Defining the tags used for categorizing routes in Swagger
home_tag = Tag(
    name="Documentation",
    description="Documentation selection: Swagger, Redoc or RapiDoc",
)
item_tag = Tag(
    name="Item",
    description=(
        "Operations for managing financial items (expenses, income, payments)."
    ),
)
label_tag = Tag(
    name="Label",
    description=(
        "Operations for managing labels (categories) for financial items."
    ),
)
recurrence_tag = Tag(
    name="Recurrence",
    description="Operations for managing recurring financial items.",
)

# Importing routes
from api.routes.home_routes import *
from api.routes.label_routes import *
from api.routes.item_routes import *
from api.routes.recurrence_routes import *


def create_app():
    """
    Factory function to create and configure the Flask application.

    This function sets up the SQLite database, configures CORS, initializes
    database tables if they don't already exist, and registers the API routes
    for managing items, labels, and recurrences.

    Returns:
        Flask app: The configured Flask application instance.
    """
    # Set up the path to the SQLite database file
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, "api", "database", "granabox.sqlite3")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(app)

    # Initialize the database with the Flask app
    db.init_app(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    # Create the Flask app and run
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
