"""REST API for exceptions."""
from flask import jsonify
import insta485


class InvalidUsage(Exception):
    """Class for invalid usage."""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """Generate an exception."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Change to dictionary."""
        reply = dict(self.payload or ())
        reply['message'] = self.message
        reply['status_code'] = self.status_code
        return reply


@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handle invalid usage."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
