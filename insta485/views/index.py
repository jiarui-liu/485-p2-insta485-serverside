"""
Insta485 index (main) view.
URLs include:
/
"""
import flask
import insta485
import arrow


def context_generator_index(logname):
    # Connect to database
    connection = insta485.model.get_db()

    # query information from post table
    # The following relation is username1 follows username2
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE owner IN (SELECT username2 FROM following WHERE username1 = ?) OR owner = ? "
        "ORDER BY postid DESC",
        (logname, logname)
    )
    # fetchall() return a list of rows
    posts = cur.fetchall()
    
    # each post is a dictionary
    for post in posts:
        # add in comments for each post
        cur = connection.execute(
            "SELECT owner, text "
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
        
    print(posts[0])
    return {"logname": logname, "posts": posts} 
        
    
@insta485.app.route('/')
def show_index():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    else:
        logname = flask.session['username']
        context = context_generator_index(logname)
        return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<path:filename>')
def upload_file(filename):
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],filename)

@insta485.app.route('/submit/', methods=['GET','POST'])
def process_submit():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    if flask.request.method == 'POST':
        operation = flask.request.form['operation']
        postid = flask.request.form['postid']
        connection = insta485.model.get_db()
        if operation == "like":
            connection.execute(
                "INSERT INTO likes(owner, postid)  VALUES (?,?)",
                (logname, postid, )
            )
        elif operation == "unlike":
            connection.execute(
                "DELETE FROM likes WHERE owner=? AND postid=?",
                (logname, postid, )
            )
        elif operation == "create":
            text = flask.request.form['text']
            connection.execute(
                "INSERT INTO comments(owner, postid, text) VALUES (?,?,?)",
                (logname, postid, text)
            )
    return flask.redirect(flask.url_for('show_index'))


