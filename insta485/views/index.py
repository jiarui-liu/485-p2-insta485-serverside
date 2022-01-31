"""
Insta485 index (main) view.
URLs include:
/
"""
import flask
import insta485
import arrow

""" generate all posts related to the logname. Namely, users the logname is following and logname itself. """
def all_posts_generator(connection, logname):
    # query information from post table
    # The following relation is username1 follows username2
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE owner IN (SELECT username2 FROM following WHERE username1 = ?) OR owner = ? "
        "ORDER BY postid DESC",
        (logname, logname,)
    )
    return cur

""" generate a single post specified by postid """
def single_posts_generator(connection, postid):
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE postid = ?",
        (postid, )
    )
    return cur

def context_generator_index(logname, postid=None):
    # Connect to database
    connection = insta485.model.get_db()



    if postid is None:
        cur = all_posts_generator(connection, logname)
    else:
        cur = single_posts_generator(connection, postid)
    
    # fetchall() return a list of rows
    posts = cur.fetchall()
    
    # each post is a dictionary
    for post in posts:
        # add in comments for each post
        cur = connection.execute(
            "SELECT commentid, owner, text "
            "FROM comments "
            "WHERE postid = ?"
            "ORDER BY created",
            (post["postid"],)
        )
        post["comments"] = cur.fetchall()
        
        # add in likes for each post
        cur = connection.execute(
            "SELECT likeid FROM likes WHERE postid = ?",
            (post["postid"],)
        )
        post["likes"] = len(cur.fetchall())
        
        # change timestamp to human readable format
        past = arrow.get(post["created"])
        present = arrow.utcnow()
        post["created"] = past.humanize(present)
        
        # add post owner's image
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (post["owner"],)
        )
        post["owner_img_url"] = cur.fetchall()[0]['filename']
        
        # see if log in user liked this post
        cur = connection.execute(
            "SELECT * FROM likes WHERE owner = ? AND postid = ?",
            (logname, post["postid"], )
        )
        post["isLiked"] = len(cur.fetchall())
        
    # print(posts[0])
    return {"logname": logname, "posts": posts} 
        
    
@insta485.app.route('/')
def show_index():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    else:
        logname = flask.session['username']
        connection = insta485.model.get_db()
        # check the logname exists in users
        cur = connection.execute(
            "SELECT * FROM users "
            "WHERE username = ?",
            (logname, )
        ).fetchall()
        if len(cur) == 0:
            flask.session.clear()
            return flask.redirect(flask.url_for('log_in_page'))
        
        # generate all posts in the root page /
        context = context_generator_index(logname)
        return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<path:filename>')
def upload_file(filename):
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],filename)

@insta485.app.route('/likes/', methods=['POST'])
def process_like():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    operation = flask.request.form['operation']
    connection = insta485.model.get_db()
    if operation == "like":
        postid = flask.request.form['postid']
        connection.execute(
            "INSERT INTO likes(owner, postid)  VALUES (?,?)",
            (logname, postid, )
        )
    elif operation == "unlike":
        postid = flask.request.form['postid']
        connection.execute(
            "DELETE FROM likes WHERE owner=? AND postid=?",
            (logname, postid, )
        )
    target = flask.request.args.get('target')
    if target is None:
        target = '/'
    return flask.redirect(target)

@insta485.app.route('/submit/', methods=['GET','POST'])
def process_submit():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    if flask.request.method == 'POST':
        operation = flask.request.form['operation']
        connection = insta485.model.get_db()
        if operation == "create":
            postid = flask.request.form['postid']
            text = flask.request.form['text']
            connection.execute(
                "INSERT INTO comments(owner, postid, text) VALUES (?,?,?)",
                (logname, postid, text)
            )
        elif operation == "delete":
            delete_comment = 'commentid' in flask.request.form.keys()
            if not delete_comment:
                postid = flask.request.form['postid']
                connection.execute(
                    "DELETE FROM comments "
                    "WHERE postid = ?",
                    (postid, )
                )
                connection.execute(
                    "DELETE FROM posts "
                    "WHERE postid = ?",
                    (postid, )
                )
            else:
                commentid = flask.request.form['commentid']
                connection.execute(
                    "DELETE FROM comments "
                    "WHERE commentid = ?",
                    (commentid, )
                )
    target = flask.request.args.get('target')
    return flask.redirect(target)


