import flask
import insta485
from werkzeug.exceptions import abort

@insta485.app.route('/users/<username>/following/')
def following_page(username):
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session["username"]
    
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM users WHERE username=?", (username,)
    ).fetchall()
    
    # check username existence
    if cur is None:
        abort(404, f'You try to access a user that does not exist.')

    cur = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?", (username,)
    ).fetchall()
    following_names = [elt['username2'] for elt in cur]
    
    following_info = []
    for following_name in following_names:
        following_dict = {}
        following_dict["username"] = following_name
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?", (following_name,)
        ).fetchall()
        following_dict["user_img_url"] = cur[0]["filename"]
        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? AND username2=?", (logname, following_name,)
        ).fetchall()
        if len(cur) == 0:
            following_dict["logname_follows_username"] = False
        else:
            following_dict["logname_follows_username"] = True
        following_info.append(following_dict)
    
    context = {"logname":logname, "following":following_info}
    return flask.render_template("following.html",**context)
