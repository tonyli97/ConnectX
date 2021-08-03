"""
Insta485 index (main) view.

URLs include:
/
"""
import os
import tempfile
import hashlib
import uuid
import shutil
import arrow
import flask
from flask import render_template, send_from_directory
from flask import url_for, session, redirect, request, abort
import insta485
from insta485.model import get_db


# --------------------------------------------------------------
# -------------------------Password-----------------------------
# --------------------------------------------------------------


@insta485.app.route('/accounts/password/', methods=['GET', 'POST'])
def password():
    """Compute password."""
    context = {}
    context['logname'] = session['username']
    database = get_db()
    cursor = database.cursor()
    if flask.request.method == 'POST':
        old_password = request.form['password']
        new_password1 = request.form['new_password1']
        new_password2 = request.form['new_password2']
        cursor.execute('SELECT * FROM users WHERE username=:u',
                       {'u': context['logname']})
        data = cursor.fetchone()
        salt = data['password'].split('$')[1]

        if sha512(salt, old_password) != data['password']:
            abort(403)
        if new_password1 != new_password2:
            abort(401)
        encry_password = sha512(salt, new_password1)
        cursor.execute('UPDATE users SET password=:p WHERE username=:u',
                       {'p': encry_password, 'u': context['logname']})
    return flask.render_template("password.html", **context)


# --------------------------------------------------------------
# ----------------------------Edit------------------------------
# --------------------------------------------------------------


def sha256sum(filename):
    """Return sha256 hash of file content, similar to UNIX sha256sum."""
    content = open(filename, 'rb').read()
    sha256_obj = hashlib.sha256(content)
    return sha256_obj.hexdigest()


def renew_photo(file):
    """Save POST request's file object to a temp file."""
    dummy, temp_filename = tempfile.mkstemp()
    file.save(temp_filename)
    # Compute filename
    hash_txt = sha256sum(temp_filename)
    dummy, suffix = os.path.splitext(file.filename)
    hash_filename_basename = hash_txt + suffix
    hash_filename = os.path.join(
        insta485.app.config["UPLOAD_FOLDER"],
        hash_filename_basename
        )
    # Move temp file to permanent location
    shutil.move(temp_filename, hash_filename)
    insta485.app.logger.debug("Saved %s", hash_filename_basename)
    return hash_filename_basename


@insta485.app.route('/accounts/edit/', methods=['GET', 'POST'])
def edit():
    """Display edit page."""
    context = {}
    context['logname'] = session['username']
    database = get_db()
    cursor = database.cursor()
    cursor.execute('SELECT * FROM users WHERE username=:name',
                   {'name': context['logname']})
    data = cursor.fetchone()
    context['user_img_url'] = url_for('uploaded_file',
                                      filename=data['filename'])
    context['user_fullname'] = data['fullname']
    context['user_email'] = data['email']
    if flask.request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        context['user_fullname'] = fullname
        context['user_email'] = email
        cursor.execute('UPDATE users SET fullname=:f, email=:e WHERE \
                       username=:u',
                       {'f': fullname, 'e': email,
                        'u': context['logname']})
        if 'file' in flask.request.files:
            cursor.execute('SELECT * FROM users WHERE username=:u',
                           {'u': context['logname']})
            data = cursor.fetchone()
            os.remove(os.path.join(insta485.app.config['UPLOAD_FOLDER'],
                                   data['filename']))
            file = flask.request.files["file"]
            hash_filename_basename = renew_photo(file)
            cursor.execute('UPDATE users SET filename=:f \
                           WHERE username=:u',
                           {'f': hash_filename_basename,
                            'u': context['logname']})
            context['user_img_url'] = url_for('uploaded_file',
                                              filename=hash_filename_basename)

    return flask.render_template("edit.html", **context)


# --------------------------------------------------------------
# ---------------------------following--------------------------
# --------------------------------------------------------------


@insta485.app.route('/u/<username>/following/', methods=['GET', 'POST'])
def following(username):
    """Display following page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    database = insta485.model.get_db()
    cursor = database.cursor()
    context = {}
    context['logname'] = flask.session['username']
    context['username'] = username
    if flask.request.method == 'POST':
        if 'unfollow' in flask.request.form:
            cursor.execute('DELETE FROM following WHERE username1=? \
                           AND username2=?',
                           (context['logname'],
                            flask.request.form['username']))
        elif 'follow' in flask.request.form:
            cursor.execute('INSERT INTO following (username1,username2) \
                           VALUES (?,?)',
                           (context['logname'],
                            flask.request.form['username']))
    cursor.execute('SELECT * FROM following WHERE username1=? AND username2=?',
                   (context['logname'], username))
    tmp = cursor.fetchone()
    if tmp:
        context['logname_follows_username'] = True
    else:
        context['logname_follows_username'] = False

    query = "SELECT * FROM users U, following F WHERE \
             U.username == F.username2 AND F.username1 =='%s'"
    cursor.execute(query % username)
    context['following'] = cursor.fetchall()
    for i in range(len(context['following'])):
        cursor.execute('SELECT * FROM following WHERE username1=? \
                       AND username2=?',
                       (context['logname'],
                        context['following'][i]['username']))
        tmp = cursor.fetchone()
        if tmp:
            context['following'][i]['logname_follows_username'] = True
        else:
            context['following'][i]['logname_follows_username'] = False
        context['following'][i]['user_img_url'] = \
            url_for('uploaded_file',
                    filename=context['following'][i]['filename'])

    return flask.render_template("following.html", **context)


# --------------------------------------------------------------
# ---------------------------followers--------------------------
# --------------------------------------------------------------


@insta485.app.route('/u/<username>/followers/', methods=['GET', 'POST'])
def followers(username):
    """Display followers page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    database = insta485.model.get_db()
    cursor = database.cursor()
    context = {}
    context['logname'] = flask.session['username']
    context['username'] = username
    if flask.request.method == 'POST':
        if 'unfollow' in flask.request.form:
            follower = flask.request.form['username']
            cursor.execute('DELETE FROM following WHERE username1=:u1 \
                           AND username2=:u2',
                           {'u1': context['logname'], 'u2': follower})
        elif 'follow' in flask.request.form:
            cursor.execute('INSERT INTO following (username1,username2) \
                           VALUES (?,?)',
                           (context['logname'],
                            flask.request.form['username']))
    context['followers'] = []

    cursor.execute('SELECT * FROM following WHERE username2=:u',
                   {'u': username})
    data = cursor.fetchall()
    for i in data:
        follower = {}
        follower['username'] = i['username1']
        cursor.execute('SELECT * FROM users WHERE username=:u',
                       {'u': i['username1']})
        pic = cursor.fetchone()
        follower['user_img_url'] = url_for('uploaded_file',
                                           filename=pic['filename'])
        cursor.execute('SELECT * FROM following WHERE username1=:u1 \
                       AND username2=:u2',
                       {'u1': context['logname'], 'u2': i['username1']})
        users = cursor.fetchall()
        follower['logname_follows_username'] = False
        if users:
            follower['logname_follows_username'] = True
        context['followers'].append(follower)

    return flask.render_template("followers.html", **context)


# --------------------------------------------------------------
# ---------------------------explore----------------------------
# --------------------------------------------------------------


@insta485.app.route('/explore/', methods=['GET', 'POST'])
def explore():
    """Display explore page."""
    context = {}
    context['logname'] = session['username']
    database = get_db()
    cursor = database.cursor()
    if flask.request.method == 'POST':
        if 'follow' in flask.request.form:
            cursor.execute('INSERT INTO following (username1,username2) \
                           VALUES (?,?)',
                           (context['logname'], request.form['username']))
    query = "SELECT U.username, U.filename FROM \
    users U WHERE U.username NOT IN(\
    SELECT DISTINCT F.username2 FROM following F WHERE F.username1 = '%s')\
     AND U.username <> '%s'"
    data = cursor.execute(query % (context['logname'], context['logname']))
    unfollow_users = data.fetchall()
    context["not_following"] = unfollow_users
    for index, user in enumerate(unfollow_users):
        context["not_following"][index]["user_img_url"] = \
            url_for('uploaded_file', filename=user['filename'])
    return flask.render_template("explore.html", **context)

# --------------------------------------------------------------
# ---------------------------post-------------------------------
# --------------------------------------------------------------


def time_calculator(past_time):
    """Compute human-readable time."""
    utc = arrow.utcnow()
    past = arrow.get(past_time)
    return past.humanize(utc)


@insta485.app.route('/p/<int:postid_in>/', methods=['GET', 'POST'])
def postid_slug(postid_in):
    """Display post."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    database = get_db()
    cursor = database.cursor()

    context = {}
    context['logname'] = flask.session['username']
    context['postid'] = postid_in
    
    # post method
    if flask.request.method == 'POST':
        if 'like' in flask.request.form:
            postid = request.form['postid']
            cursor.execute('INSERT INTO likes (owner, postid) VALUES (?, ?)',
                           (session['username'], postid))
        elif 'unlike' in flask.request.form:
            postid = request.form['postid']
            cursor.execute('DELETE FROM likes WHERE (owner = ? AND\
                           postid = ?)', (session['username'], postid))
        elif 'delete' in flask.request.form:
            cursor.execute("DELETE FROM posts WHERE postid=:id",
                           {'id': postid_in})
            return flask.redirect(flask.url_for("show_index"))
        elif 'uncomment' in flask.request.form:
            commentid = request.form['commentid']
            cursor.execute('DELETE FROM comments WHERE commentid=:id',
                           {'id': commentid})
        elif 'comment' in flask.request.form:
            postid = request.form['postid']
            text = request.form['text']
            cursor.execute('INSERT INTO comments (owner,postid,text) VALUES \
                           (?,?,?)', (session['username'], postid, text))

    cursor.execute('SELECT * FROM posts WHERE postid=:id', {'id': postid_in})
    data = cursor.fetchone()

    context['owner'] = data['owner']
    context['timestamp'] = time_calculator(data['created'])
    context['img_url'] = url_for('uploaded_file', filename=data['filename'])
    cursor.execute('SELECT * FROM users WHERE username=:user',
                   {'user': context['owner']})
    picture = cursor.fetchone()
    context['owner_img_url'] = url_for('uploaded_file',
                                       filename=picture['filename'])

    cursor.execute('SELECT * FROM likes WHERE postid=:id', {'id': postid_in})
    data = cursor.fetchall()
    context['likes'] = len(data)
    does_like = False
    for i in data:
        if i['owner'] == context['logname']:
            does_like = True
    context['does_like'] = does_like

    context['comments'] = []
    cursor.execute('SELECT * FROM comments WHERE postid=:id',
                   {'id': postid_in})
    data = cursor.fetchall()
    for datum in data:
        diction = {}
        diction['owner'] = datum['owner']
        diction['text'] = datum['text']
        diction['commentid'] = datum['commentid']
        context['comments'].append(diction)

    return flask.render_template("post.html", **context)


# --------------------------------------------------------------
# ---------------------------user-------------------------------
# --------------------------------------------------------------
@insta485.app.route('/u/<username>/', methods=['GET', 'POST'])
def show_user(username):
    """Display user page."""
    context = {}
    context['posts'] = []
    context['logname'] = session['username']
    database = get_db()
    cursor = database.cursor()
    if request.method == 'POST':
        if 'unfollow' in flask.request.form:
            cursor.execute('DELETE FROM following\
                           WHERE username1=? AND username2=?',
                           (context['logname'], username))
        elif 'follow' in flask.request.form:
            cursor.execute('INSERT INTO following (username1,username2)\
                           VALUES (?,?)', (context['logname'], username))
        elif 'create_post' in flask.request.form:
            file = flask.request.files["file"]
            filename = renew_photo(file)
            cursor.execute('INSERT INTO posts(filename, owner) \
                           VALUES (?,?)', (filename, username))
            
    
    cursor.execute('SELECT * FROM users WHERE username=:user',
                   {'user': username})
    data = cursor.fetchone()
    context['username'] = data['username']
    context['fullname'] = data['fullname']
    cursor.execute('SELECT * FROM following WHERE username2=:user',
                   {'user': username})
    fans = cursor.fetchall()
    context['followers'] = str(len(fans))
    context['logname_follows_username'] = False
    for i in fans:
        if context['logname'] == i['username1']:
            context['logname_follows_username'] = True
    cursor.execute('SELECT * FROM following WHERE username1=:user',
                   {'user': username})
    idols = cursor.fetchall()
    context['following'] = str(len(idols))
    cursor.execute('SELECT * FROM posts WHERE owner=:user',
                   {'user': username})
    rows = cursor.fetchall()
    context['total_posts'] = str(len(rows))
    for row in rows:
        post = {}
        post['postid'] = str(row['postid'])
        post['img_url'] = url_for('uploaded_file', filename=row['filename'])
        post['owner'] = row['owner']
        post['timestamp'] = time_calculator(row['created'])
        context['posts'].append(post)
    return flask.render_template("user.html", **context)

# --------------------------------------------------------------
# ---------------------------delete-----------------------------
# --------------------------------------------------------------


@insta485.app.route('/accounts/delete/', methods=['GET', 'POST'])
def delete():
    """Display delete page."""
    if request.method == 'POST':
        database = get_db()
        cursor = database.cursor()
        cursor.execute('SELECT * FROM users WHERE username=:u',
                       {'u': session['username']})
        data = cursor.fetchone()
        os.remove(os.path.join(insta485.app.config['UPLOAD_FOLDER'],
                               data['filename']))
        cursor.execute('SELECT * FROM posts WHERE owner=:u',
                       {'u': session['username']})
        data = cursor.fetchall()
        for i in data:
            os.remove(os.path.join(insta485.app.config['UPLOAD_FOLDER'],
                                   i['filename']))
        cursor.execute('DELETE FROM users WHERE username=:user',
                       {'user': session['username']})
        session.clear()
        return redirect(url_for('create'))
    context = {}
    context['logname'] = session['username']
    return flask.render_template("delete.html", **context)

# --------------------------------------------------------------
# ---------------------------create-----------------------------
# --------------------------------------------------------------


def sha512(salt, in_password):
    """Encrypt the password."""
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + str(in_password)
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


@insta485.app.route('/accounts/create/', methods=['GET', 'POST'])
def create():
    """Display create page."""
    context = {}
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit'))
    if request.method == 'POST':
        file = flask.request.files["file"]
        filename = renew_photo(file)
        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        input_password = request.form['password']
        if input_password == '':
            abort(400)
        database = get_db()
        cursor = database.cursor()
        cursor.execute('SELECT * FROM users WHERE username=:user',
                       {'user': username})
        data = cursor.fetchone()
        if data:
            abort(409)
        session['username'] = username
        salt = str(uuid.uuid4().hex)
        encry_password = sha512(salt, input_password)
        cursor.execute('INSERT INTO users(username, fullname, email, \
                       filename, password) VALUES (?,?,?,?,?)',
                       (username, fullname, email, filename,
                        encry_password))
        return redirect(url_for('show_index'))

    return flask.render_template("create.html", **context)

# --------------------------------------------------------------
# ---------------------------logout-----------------------------
# --------------------------------------------------------------


@insta485.app.route('/accounts/logout/')
def log_out():
    """Display logout page."""
    session.clear()
    return redirect(url_for('show_login'))


# --------------------------------------------------------------
# ---------------------------show_login-------------------------
# --------------------------------------------------------------


@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def show_login():
    """Display login page."""
    context = {}
    if request.method == 'POST':
        username = request.form['username']
        input_password = request.form['password']
        database = get_db()
        cursor = database.cursor()
        cursor.execute('SELECT * FROM users WHERE username=:user',
                       {'user': username})
        data = cursor.fetchone()
        if data is None:
            return redirect(url_for('show_login'))
        salt = data['password'].split('$')[1]
        encry_password = sha512(salt, input_password)
        if data['password'] == encry_password:
            session['username'] = username
            return redirect(url_for('show_index'))

    return flask.render_template("login.html", **context)


@insta485.app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Upload pictures."""
    return send_from_directory(insta485.app.config['UPLOAD_FOLDER'], filename)


@insta485.app.route('/', methods=["GET", "POST"])
def show_index():
    """Display / route."""
    if 'username' not in session:
        return redirect(url_for('show_login'))
    context = {}
    context['logname'] = session['username']
    database = get_db()
    cursor = database.cursor()
    if request.method == "POST":
        postid = request.form['postid']
        if 'like' in request.form:
            cursor.execute('INSERT INTO likes (owner, postid) VALUES (?, ?)',
                           (session['username'], postid))
        elif 'unlike' in request.form:
            cursor.execute('DELETE FROM likes WHERE (owner = ? AND \
                           postid = ?)', (session['username'], postid))
        elif 'comment' in request.form:
            text = request.form['text']
            cursor.execute('INSERT INTO comments (owner,postid,text) VALUES \
                           (?,?,?)', (session['username'], postid, text))

    posts = []
    cursor.execute('SELECT * FROM following WHERE username1=:logname',
                   {'logname': context['logname']})
    rows = cursor.fetchall()
    friends = []
    for i in rows:
        friends.append(i['username2'])
    friends.append(context['logname'])

    cursor.execute('SELECT * FROM posts')
    rows = cursor.fetchall()
    for row in rows:
        if row['owner'] not in friends:
            continue
        post = {}
        post['postid'] = row['postid']
        post['img_url'] = url_for('uploaded_file', filename=row['filename'])
        post['owner'] = row['owner']
        post['timestamp'] = time_calculator(row['created'])

        cursor.execute('SELECT * FROM users WHERE username=:owner',
                       {'owner': row['owner']})
        post['owner_img_url'] = url_for('uploaded_file',
                                        filename=cursor.fetchone()['filename'])
        cursor.execute('SELECT * FROM comments WHERE postid=:id',
                       {'id': row['postid']})
        data = cursor.fetchall()
        comments = []
        for i in data:
            comment = {}
            comment['owner'] = i['owner']
            comment['text'] = i['text']
            comments.append(comment)
        post['comments'] = comments

        cursor.execute('SELECT * FROM likes WHERE postid=:id',
                       {'id': row['postid']})
        data = cursor.fetchall()
        post['likes'] = len(data)
        does_like = False
        for i in data:
            if i['owner'] == context['logname']:
                does_like = True
                break
        post['does_like'] = does_like

        posts.append(post)

    context['posts'] = posts

    return render_template("index.html", **context)
