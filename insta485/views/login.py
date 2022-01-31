"""
Insta485 login page view.
URLs include:
/accounts/login/, /accounts/logout/
"""


import flask
import insta485


@insta485.app.route('/accounts/login/', methods=('GET','POST'))
def log_in_page():
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        connection = insta485.model.get_db()
        error = None
        cur = connection.execute(
            'SELECT password FROM users WHERE username=?',
            (username,)
        ).fetchall()
        
        if len(cur) == 0:
            error = 'Incorrect username'
        else:
            correct_password = cur[0]['password']
            if correct_password != password:
                error = 'Incorrect password'
            else:
                flask.session.clear()
                flask.session['username'] = username
                return flask.redirect(flask.url_for('show_index'))
            flask.flash(error)
    return flask.render_template('login.html')

""" the endpoint only accepts `POST` requests """
@insta485.app.route('/accounts/logout/', methods=['POST'])
def log_out_page():
    flask.session.clear()
    return flask.redirect(flask.url_for('log_in_page'))
