"""
Insta485 index (main) view.
URLs include:
/
"""
import flask
import insta485
import arrow


# @insta485.app.route('/')
# def show_index():
#     """Display / route."""
#     # Connect to database
#     connection = insta485.model.get_db()
#     # Query database
#     logname = "awdeorio"
#     cur = connection.execute(
#         "SELECT username, fullname "
#         "FROM users "
#         "WHERE username != ?",
#         (logname, )
#     )
#     users = cur.fetchall()
#     # Add database info to context
#     context = {"users": users}
#     return flask.render_template("index.html", **context)


def context_generator(logname):
    # Connect to database
    connection = insta485.model.get_db()

    # query information from post table
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE owner IN (SELECT username2 FROM following WHERE username1 = ?) OR owner = ? "
        "ORDER BY postid DESC",
        (logname, logname)
    )
    posts = cur.fetchall()
    
    
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
    # if 'username' not in flask.session:
    #     return flask.redirect(flask.url_for('log_in_page'))
    # else:
    #     logname = flask.session['usename']
    #     context = context_generator(logname)
        
    context = context_generator('awdeorio')
    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<path:filename>')
def download_file(filename):
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],filename)
