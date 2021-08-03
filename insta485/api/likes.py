"""REST API for likes."""
import flask
import insta485
from insta485.api.exception import InvalidUsage


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/', methods=["GET"])
def get_likes(postid_url_slug):
    """Return likes on postid.

    Example:
    {
        "logname_likes_this": 1,
        "likes_count": 3,
        "postid": 1,
        "url": "/api/v1/p/1/likes/"
    }
    """
    if "username" not in flask.session:
        raise InvalidUsage('Forbidden', status_code=403)

    # User
    logname = flask.session["username"]
    context = {}

    # url
    context["url"] = flask.request.path

    # Post
    postid = postid_url_slug
    context["postid"] = postid

    # Did this user like this post?
    connection = insta485.model.get_db()
    cursor = connection.execute("SELECT * FROM posts \
                                WHERE postid = ?", (postid,))
    if bool(cursor.fetchone()) is False:
        raise InvalidUsage('Not Found', status_code=404)
    cursor = connection.execute(
        "SELECT EXISTS( "
        "  SELECT 1 FROM likes "
        "    WHERE postid = ? "
        "    AND owner = ? "
        "    LIMIT 1"
        ") AS logname_likes_this ",
        (postid, logname)
    )
    data = cursor.fetchone()

    context['logname_likes_this'] = data['logname_likes_this']

    # Likes
    cursor = connection.execute(
        "SELECT COUNT(*) AS likes_count FROM likes WHERE postid = ? ",
        (postid,)
    )

    data = cursor.fetchone()
    context['likes_count'] = data['likes_count']

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<int:postid_url>/likes/', methods=["DELETE"])
def delete_likes(postid_url):
    """Return likes on postid.

    Example:
    {
        "logname_likes_this": 1,
        "likes_count": 3,
        "postid": 1,
        "url": "/api/v1/p/1/likes/"
    }
    """
    if "username" not in flask.session:
        raise InvalidUsage('Forbidden', status_code=403)

    # User
    logname = flask.session["username"]
    context = {}

    # url
    context["url"] = flask.request.path

    # Post
    postid = postid_url
    context["postid"] = postid

    connection = insta485.model.get_db()
    connection.execute(
        "DELETE FROM likes "
        "    WHERE postid = ? "
        "    AND owner = ? ",
        (postid, logname)
    )
    response = flask.make_response('', 204)
    response.headers['Content-length'] = 0
    response.headers['Content-type'] = 'application/json'
    return response


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/', methods=["POST"])
def post_likes(postid_url_slug):
    """Return likes on postid.

    Example:
    {
        "logname_likes_this": 1,
        "likes_count": 3,
        "postid": 1,
        "url": "/api/v1/p/1/likes/"
    }
    """
    if "username" not in flask.session:
        raise InvalidUsage('Forbidden', status_code=403)

    # User
    logname = flask.session["username"]
    context = {}
    context['logname'] = logname

    # Post
    postid = postid_url_slug
    context["postid"] = postid

    connection = insta485.model.get_db()
    cursor = connection.execute('SELECT count(*) FROM likes \
                                WHERE postid = ? AND owner = ?',
                                (postid, logname)).fetchone()
    if(cursor['count(*)']) > 0:
        context['message'] = "Conflict"
        context['status_code'] = 409
        return flask.jsonify(**context), 409

    cursor = connection.execute(
        "INSERT INTO likes (owner, postid)"
        "SELECT ?,? WHERE NOT EXISTS (SELECT * FROM \
        likes WHERE postid = ? AND owner = ?)",
        (logname, postid, postid, logname)
    )
    response = flask.make_response('', 201)
    response.headers['Content-type'] = 'application/json'
    return flask.jsonify(**context), 201
