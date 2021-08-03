"""REST API for posts_details."""
import flask
import insta485
from insta485.api.exception import InvalidUsage


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/', methods=["GET"])
def get_post_details(postid_url_slug):
    """Return the details for one post."""
    context = {}
    if "username" not in flask.session:
        raise InvalidUsage('Forbidden', status_code=403)

    # url
    context["url"] = '/api/v1/p/' + str(postid_url_slug) + '/'

    connection = insta485.model.get_db()
    cursor = connection.execute(
        "SELECT * FROM posts WHERE postid=:id", {'id': postid_url_slug})
    post_info = cursor.fetchone()
    if bool(post_info) is False:
        raise InvalidUsage('Not Found', status_code=404)

    context['age'] = post_info['created']
    context['img_url'] = '/uploads/' + post_info['filename']
    context['owner'] = post_info['owner']
    context['owner_show_url'] = '/u/' + post_info['owner'] + '/'
    context['post_show_url'] = '/p/' + str(postid_url_slug) + '/'
    cursor = connection.execute(
        "SELECT filename FROM users WHERE username=:n",
        {'n': post_info['owner']})
    user_file = cursor.fetchone()
    context['owner_img_url'] = '/uploads/' + user_file['filename']

    return flask.jsonify(**context)
