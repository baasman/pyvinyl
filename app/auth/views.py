import os
import sys

from flask import request, redirect, render_template, flash, url_for, abort
from flask import current_app as capp
from flask_login import login_user, logout_user, login_required

from app.models import User
from app.user_management import FlaskUser
from . import auth
from .forms import LoginForm, RegistrationForm, LastfmAuthForm

import pylast


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST': # and form.validate_on_submit():
        user = User.objects.get(user=form.user.data)
        if user and User.validate_login(user['password_hash'], form.password.data):
            user_obj = FlaskUser(user['user'])
            login_user(user_obj)
            flash('Logged in successfully. Happy scrobbling', category='success')
            return redirect(url_for('collection.collection_page', username=user['user']))
        else:
            flash('Password does not match username', category='error')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if request.method == 'POST' and reg_form.validate_on_submit():
        user = User(email=reg_form.email.data,
                    username=reg_form.username.data,
                    lastfm_user=reg_form.lastfm_user.data)
        user.lastfm_password = user.generate_lfm_hash(reg_form.lastfm_password.data)
        user.password_hash = user.set_password(reg_form.password.data)
        try:
            n = user.save()
            login_user(user)
            if user.lastfm_password and user.lastfm_user:
                return redirect(url_for('auth.lastfm_setup', username=user.username))

            flash('Thanks for registering')
            return redirect(url_for('collection.collection_page', username=user.username))
        except:
            print(sys.exc_info()[:2])
    return render_template('auth/register.html', form=reg_form)

@auth.route('/u/<username>/lastfm_setup', methods=['GET', 'POST'])
@login_required
def lastfm_setup(username):
    user = User.objects.get(user=username)

    fm_form = LastfmAuthForm()

    client = pylast.LastFMNetwork(capp.config['LASTFM_API_KEY'],
                                      capp.config['LASTFM_API_SECRET'])
    sk = pylast.SessionKeyGenerator(client)
    url = sk.get_web_auth_url()

    user.update(set__lastfm_token_url=url, upsert=True)

    if request.method == 'POST' and fm_form.confirm.data:

        skey = sk.get_session_key(user['lastfm_username'],
                                  user['lastfm_password'])

        user.update(set__lfm_is_authenticated=True, upsert=True)
        user.update(set__lfm_session_key=skey, upsert=True)

        return redirect(url_for('collection.collection_page', username=username))
    return render_template('auth/lastfm_setup.html', fm_form=fm_form, url=url)

@auth.route('/logout')
def logout():
    username = request.args.get('username')
    tmp_files = os.listdir(os.path.join(capp.static_folder, 'tmp'))
    for file in tmp_files:
        try:
            os.remove(os.path.join(capp.static_folder, 'tmp', file))
        except:
            print(sys.exc_info()[:2])

    # TODO: figure out how to use pull_all
    n = User.objects.get(user=username).update(
        set__tmp_files=[]
    )
    logout_user()
    return redirect(url_for('home.homepage'))