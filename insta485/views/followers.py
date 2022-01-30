import flask
import insta485

@insta485.app.route('/users/<username>/followers/')
def followers_page(username):
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session["username"]
    
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username1 FROM following WHERE username2 = ?", (logname,)
    ).fetchall()
    usernames = [elt['username1'] for elt in cur]
    
    followers_info = []
    for username in usernames:
        follower_dict = {}
        follower_dict["username"] = username
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?", (username,)
        ).fetchall()
        follower_dict["user_img_url"] = cur[0]["filename"]
        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? AND username2=?", (logname, username,)
        ).fetchall()
        if len(cur) == 0:
            follower_dict["logname_follows_username"] = False
        else:
            follower_dict["logname_follows_username"] = True
        followers_info.append(follower_dict)
    
    context = {"logname":logname, "followers":followers_info}
    return flask.render_template("followers.html",**context)
        
    
    