"""REST API for services."""
import flask
import insta485
from insta485.api.exception import InvalidUsage


@insta485.app.route('/api/v1/', methods=["GET"])
def get_services():
    """Get services."""
    if "username" not in flask.session:
        raise InvalidUsage('Forbidden', status_code=403)

    context = {}
    context['posts'] = "/api/v1/p/"
    context["url"] = flask.request.path

    return flask.jsonify(**context)
