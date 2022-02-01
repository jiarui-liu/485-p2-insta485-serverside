"""
Insta485 login page view.
URLs include:
/accounts/login/, /accounts/logout/
"""


import flask
import insta485

""" GET /accounts/login/ """


@insta485.app.route('/accounts/login/')
def log_in_page():
    return flask.render_template('login.html')


""" POST /accounts/logout/ """


@insta485.app.route('/accounts/logout/', methods=['POST'])
def log_out_page():
    # whether or not username is in the session does not matter
    flask.session.clear()
    return flask.redirect(flask.url_for('log_in_page'))
