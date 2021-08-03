"""REST API for comments."""
import flask
import insta485
from insta485.api.exception import InvalidUsage


@insta485.app.route('/api/v1/p/<int:postid>/comments/',
                    methods=["GET", "POST"])
def comment(postid):
    """Return the details for one post."""
    context = {}
    if "username" not in flask.session:
        raise InvalidUsage('Forbidden', status_code=403)

    connection = insta485.model.get_db()
    cursor = connection.execute(
        "SELECT * FROM comments WHERE postid=:id", {'id': postid})
    comments = cursor.fetchall()
    ''' 
    if bool(comments) is False:
        raise InvalidUsage('Not Found', status_code=404)
    '''
    # User
    logname = flask.session["username"]

    if flask.request.method == 'POST':
        data = flask.request.get_json(force=True)
        context['text'] = data['text']
        context['owner'] = logname
        context['owner_show_url'] = '/u/' + logname + '/'
        connection.execute('INSERT INTO comments (owner, postid, text) \
                           VALUES (?,?,?)', (logname, postid, data['text']))
        cursor = connection.execute('SELECT last_insert_rowid() AS id')
        commentid_dic = cursor.fetchone()
        context['commentid'] = commentid_dic['id']
        context['postid'] = postid
        return flask.jsonify(**context), 201

    # url
    context["url"] = flask.request.path
    context['comments'] = []

    for i in comments:
        one_comment = {}
        one_comment['commentid'] = i['commentid']
        one_comment['owner'] = i['owner']
        one_comment['owner_show_url'] = '/u/' + i['owner'] + '/'
        one_comment['postid'] = postid
        one_comment['text'] = i['text']
        context['comments'].append(one_comment)

    return flask.jsonify(**context)
