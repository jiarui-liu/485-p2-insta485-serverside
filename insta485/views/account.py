"""
Insta485 account-related pages view.
URLs include:
/accounts/create/, /accounts/delete/, /accounts/edit/
"""

import os
import flask
import insta485
from werkzeug.utils import secure_filename


@insta485.app.route('/accounts/create/', methods=('GET', 'POST'))
def create_page():
    # if a user is already logged in, redirect to /accounts/edit/
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit_page'))
    # process POST requests
    if flask.request.method == 'POST':
        connection = insta485.model.get_db()
        file = flask.request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
        fullname = flask.request.form['fullname']
        username = flask.request.form['username']
        email = flask.request.form['email']
        password = flask.request.form['password']
        connection.execute(
            "INSERT INTO users(username, fullname, email, filename, password) VALUES (?, ?, ?, ?, ?)",
            (username, fullname, email, filename, password)
        )
        target = flask.request.args.get('target')
        return flask.redirect(target)
    return flask.render_template('create.html')


@insta485.app.route('/accounts/delete/', methods=('GET', 'POST'))
def delete_page():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    else:
        logname = flask.session['username']
        context = {"logname": logname}
    if flask.request.method == 'POST':
        operation = flask.request.form['operation']
        connection = insta485.model.get_db()
        if operation == "delete":
            # select this user's posts
            postid_list = connection.execute(
                "SELECT postid FROM posts WHERE owner = ?", (logname, )
            ).fetchall()
            # delete related likes to this user from likes table
            for postid in postid_list:
                connection.execute(
                    "DELETE FROM likes WHERE postid = ?", (postid['postid'], )
                )
            # delete this user from likes table
            connection.execute(
                "DELETE FROM likes WHERE "
                "owner = ?", (logname, )
            )
            # delete related comments to this user from comment table
            for postid in postid_list:
                connection.execute(
                    "DELETE FROM comments WHERE postid = ?", (postid['postid'], )
                )
            # delete this user from comment table
            connection.execute(
                "DELETE FROM comments WHERE "
                "owner = ?", (logname, )
            )
            # delete filename
            filename = connection.execute(
                "SELECT filename FROM posts WHERE "
                "owner = ?", (logname, )
            ).fetchall()[0]['filename']
            os.remove(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
            # delete this user from posts table
            connection.execute(
                "DELETE FROM posts WHERE "
                "owner = ?", (logname, )
            )
            # delete this user from following table
            connection.execute(
                "DELETE FROM following WHERE "
                "username1 = ? OR username2 = ?", 
                (logname, logname, )
            )
            # delete filename
            filename = connection.execute(
                "SELECT filename FROM users WHERE "
                "username = ?", (logname, )
            ).fetchall()[0]['filename']
            os.remove(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
            # delete this user from user table
            connection.execute(
                "DELETE FROM users WHERE "
                "username = ?", (logname, )
            )
            # clear session
            flask.session.clear()
        target = flask.request.args.get('target')
        return flask.redirect(target)
    return flask.render_template('delete.html', **context)


@insta485.app.route('/accounts/edit/', methods=('GET', 'POST'))
def edit_page():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    context = {"logname": logname}
    connection = insta485.model.get_db()
    user_info = connection.execute(
        "SELECT fullname, email, filename FROM users "
        "WHERE username = ?",
        (logname, )
    ).fetchall()
    context["user_info"] = user_info
    if flask.request.method == 'POST':
        file = flask.request.files['file']
        fullname = flask.request.form['fullname']
        email = flask.request.form['email']
        filename = secure_filename(file.filename)
        if filename is not None:
            try:
                file.save(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
                operation = flask.request.form['operation']
                if operation == "edit_account":
                    connection.execute(
                        "UPDATE users "
                        "SET filename = ?, fullname = ?, email = ? "
                        "WHERE username = ?", (filename, fullname, email, logname, )
                    )
            except Exception:
                error = 'exception occurred when uploading the file.'
        else:
            error='Please upload a photo.'
        flask.flash(error)
        target = flask.request.args.get('target')
        return flask.redirect(target)
    return flask.render_template('edit.html', **context)

@insta485.app.route('/accounts/password/', methods=('GET', 'POST'))
def password_page():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    context = {"logname": logname}
    connection = insta485.model.get_db()
    if flask.request.method == 'POST':
        password = flask.request.form['password']
        new_password1 = flask.request.form['new_password1']
        new_password2 = flask.request.form['new_password2']
        real_old_password = connection.execute(
            "SELECT password FROM users WHERE username = ?",(logname, )
        ).fetchall()[0]['password']
        if password != real_old_password:
            error = 'Incorrect old password'
        elif new_password1 != new_password2:
            error = 'Two new passwords mismatch'
        else:
            connection.execute(
                "UPDATE users "
                "SET password = ? "
                "WHERE username = ?",
                (new_password1, logname, )
            )
            target = flask.request.args.get('target')
            return flask.redirect(target)
        flask.flash(error)
    return flask.render_template('password.html', **context)