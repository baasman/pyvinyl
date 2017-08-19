import os
import sys

from flask import request, redirect, render_template, flash, url_for, abort
from flask import current_app as capp
from flask_login import login_user, logout_user

from app import login_manager, mongo
from app.user_management import User
from . import auth
from .forms import LoginForm, RegistrationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST': # and form.validate_on_submit():
        user = mongo.db.users.find_one({'user': form.user.data})
        if user and User.validate_login(user['password_hash'], form.password.data):
            user_obj = User(user['user'])
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
        user_obj = User(email=reg_form.email.data,
                        username=reg_form.username.data,
                        lastfm_user=reg_form.lastfm_user.data,
                        lastfm_password=reg_form.lastfm_password.data)
        user_obj.set_password(reg_form.password.data)
        try:
            n = mongo.db.users.insert_one({'user': user_obj.username,
                                          'email': user_obj.email,
                                          'password_hash': user_obj.password_hash,
                                           'lastfm_username': user_obj.lastfm_user,
                                           'lastfm_password': user_obj.lastfm_password,
                                           'records': [],
                                           'tmp_files': [],
                                           'discogs_info': {'oath_token': None,
                                                            'token': None,
                                                            'secret': None}})
            login_user(user_obj)
            flash('Thanks for registering')
            return redirect(url_for('collection.collection_page', username=user_obj.username))
        except:
            print(sys.exc_info()[:2])
    return render_template('auth/register.html', form=reg_form)


@auth.route('/logout')
def logout():
    username = request.args.get('username')
    tmp_files = os.listdir(os.path.join(capp.static_folder, 'tmp'))
    for file in tmp_files:
        print(os.path.join(capp.static_folder, 'tmp', file))
        try:
            os.remove(os.path.join(capp.static_folder, 'tmp', file))
        except:
            print(sys.exc_info()[:2])
    n = mongo.db.users.update({'user': username},
                              {'$set': {'tmp_files': []}})
    logout_user()
    return redirect(url_for('home.homepage'))