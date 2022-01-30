"""
Insta485 login page view.
URLs include:
/users/<user_url_slug>
"""


import flask
import insta485
import os
from werkzeug.utils import secure_filename

def context_generator_users(logname, username):
    connection = insta485.model.get_db()
    context = {}
    context["logname"], context["username"] = logname, username
    
    # get fullname
    cur = connection.execute(
        "SELECT fullname FROM users WHERE username=?", (username,)
    ).fetchall()
    context["fullname"] = cur[0]["fullname"]
    
    # get following number
    cur = connection.execute(
        "SELECT username2 FROM following WHERE username1=?", (username, )
    ).fetchall()
    context["following"] = len(cur)
    
    # get follower number
    cur = connection.execute(
        "SELECT username1 FROM following WHERE username2=?", (username,)
    ).fetchall()
    context["followers"] = len(cur)
    
    # get logname_follows_username
    cur = connection.execute(
        "SELECT * FROM following WHERE username1=? AND username2=?", (logname, username,)
    ).fetchall()
    print(cur)
    if len(cur) == 0:
        context["logname_follows_username"] = False
    else:
        context["logname_follows_username"] = True
    print(context["logname_follows_username"])
        
    # get posts information
    posts = connection.execute(
        "SELECT postid, filename FROM posts WHERE owner=?", (username,)
    ).fetchall()
    context["total_posts"] = len(posts)
    context["posts"] = posts
    
    return context


@insta485.app.route('/users/<username>/')
def user_page(username):
    
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    else:
        logname = flask.session['username']
        context = context_generator_users(logname,username)
        return flask.render_template("user.html", **context)
    
    
@insta485.app.route('/operation/user/',methods=['GET','POST'])
def operation():
    logname = flask.session['username']
    if flask.request.method == 'POST':
        operation = flask.request.form['operation']
        connection = insta485.model.get_db()
        if operation == "follow":
            username = flask.request.form['username']
            connection.execute(
                "INSERT INTO following(username1, username2) VALUES (?,?) ", (logname, username)
            )
            return flask.redirect('/users/' + username + '/')
        elif operation == "unfollow":
            print("unfollow")
            username = flask.request.form['username']
            connection.execute(
                "DELETE FROM following WHERE username1 = ? AND username2 = ?", (logname, username)
            )
            return flask.redirect('/users/' + username + '/')
        elif operation == "create":
            file = flask.request.files['file']
            if file is not None:
                filename = secure_filename(file.filename)
                file.save(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
                connection.execute(
                    "INSERT INTO posts(filename, owner) VALUES (?,?)", (filename, logname)
                )
    return flask.redirect('/users/' + logname + '/')
    