"""REST API for likes."""
import flask
import insta485
from insta485.api.exception import InvalidUsage


@insta485.app.route('/api/v1/p/', methods=["GET"])
def get_posts():
    """Return posts."""
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    postid_lte = flask.request.args.get("postid_lte", default= float('inf'), type=int)
    print (postid_lte)
    context = {}
    if "username" not in flask.session:
        raise InvalidUsage('Forbidden', status_code=403)
    if size < 0 or page < 0 or postid_lte < 0:
        raise InvalidUsage('Bad Request', status_code=400)

    # User
    logname = flask.session["username"]

    # url
    context["url"] = flask.request.path
    context['next'] = ""
    context['results'] = []

    connection = insta485.model.get_db()
    cursor = connection.execute(
        "SELECT postid FROM posts WHERE owner = ? OR owner IN \
        (SELECT username2 FROM following WHERE username1 = ?)",
        (logname, logname))
    postid_dir = cursor.fetchall()

    postid_list = []
    for i in postid_dir:
        if i['postid'] <= postid_lte:
            postid_list.append(i['postid'])
    postid_list.sort(reverse=True)



    if len(postid_list) > size * page:
        for i in range(size * page, size * page + size):
            if i < len(postid_list):
                result = {}
                result['postid'] = postid_list[i]
                result['url'] = context["url"] + str(postid_list[i]) + '/'
                context['results'].append(result)

    
    if size * page + size < len(postid_list):
        context['next'] = context["url"] + '?size=' + \
            str(size) + '&page=' + str(page + 1)
    else:
        context['next'] = context["url"] + '?size=' + \
            str(size) + '&page=' + str(0)

    return flask.jsonify(**context)

