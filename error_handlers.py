from flask import jsonify


def register_error_handlers(app):
    """
    Registers common HTTP error handlers with the Flask app.

    This function defines and registers error handlers for various HTTP error
    codes, ensuring that they return structured error responses in line with
    the ValidationErrorSchema.

    Parameters:
    - app: The Flask application instance to register error handlers with.
    """

    @app.errorhandler(400)
    def bad_request_error(error):
        """
        Handles 400 Bad Request errors.

        Returns:
        - 400: Validation error with the correct schema format.
        """
        response = {
            "loc": ["field_name"],
            "msg": "Bad Request. Please check the input data.",
            "type_": "validation_error",
        }
        return jsonify(response), 400

    @app.errorhandler(404)
    def not_found_error(error):
        """
        Handles 404 Not Found errors.

        Returns:
        - 404: Not found error with the correct schema format.
        """
        response = {
            "loc": ["resource"],
            "msg": "Resource not found.",
            "type_": "not_found",
        }
        return jsonify(response), 404

    @app.errorhandler(422)
    def unprocessable_entity_error(error):
        """
        Handles 422 Unprocessable Entity errors.

        Returns:
        - 422: Unprocessable entity error with the correct schema format.
        """
        response = {
            "loc": ["field_name"],
            "msg": (
                "Unprocessable Entity. The request is well-formed but "
                "cannot be processed."
            ),
            "type_": "validation_error",
        }
        return jsonify(response), 422
