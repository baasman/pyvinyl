from app import *
from user_management import LoginForm, RegistrationForm, DiscogsForm, User

from flask import request, redirect, render_template, flash, url_for
from flask_login import login_user, logout_user, login_required

import sys


@login_manager.user_loader
def load_user(user):
    user = mongo.db.users.find_one({'user': user})
    if user:
        return User(username=user['user'])
    else:
        return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST': # and form.validate_on_submit():
        user = mongo.db.users.find_one({'user': form.user.data})
        if user and User.validate_login(user['password_hash'], form.password.data):
            user_obj = User(user['user'])
            login_user(user_obj)
            flash('Logged in successfully. Happy scrobbling', category='success')
            return redirect(url_for('collection', username=user['user']))
        else:
            flash('Password does not match username', category='error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if request.method == 'POST' and reg_form.validate_on_submit():
        user_obj = User(email=reg_form.email.data,
                        username=reg_form.username.data,
                        discogs_user=reg_form.discogs_user.data)
        user_obj.set_password(reg_form.password.data)
        try:
            n = mongo.db.users.insert_one({'user': user_obj.username,
                                          'email': user_obj.email,
                                          'password_hash': user_obj.password_hash,
                                           'discogs_user': user_obj.discogs_user,
                                           'records': []})
            login_user(user_obj)
            flash('Thanks for registering')
            return redirect(url_for('collection', username=user_obj.username))
        except:
            print(sys.exc_info()[:2])
    return render_template('register.html', form=reg_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/collection/<username>')
@login_required
def collection(username):
    user = mongo.db.users.find_one({'user': username})

    return render_template('collection.html', username=username, user=user,
                           client=dclient)

@app.route('/discogs_setup/<username>')
def discogs_setup(username):
    args = dict(request.args)
    token, secret, url = args['tokens']
    n = mongo.db.users.update({'user': username},
                              {'$set': {'discogs_info':
                                            {'token': token,
                                            'secret': secret}}})
    print(url)
    return render_template('discogs_signup.html', url=url)
    # dform = DiscogsForm()
    # user = mongo.db.users.find_one({'user': username})
    # token, secret, url = dclient.get_authorize_url()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')