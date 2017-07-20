from app import *
from user_management import User
from forms import LoginForm, RegistrationForm, DiscogsValidationForm, AddRecordForm

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
                                           'records': [323],
                                           'discogs_info': {'oath_token': None,
                                                            'token': None,
                                                            'secret': None}})
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

@app.route('/discogs_setup/<username>', methods=['GET', 'POST'])
@login_required
def discogs_setup(username):
    args = dict(request.args)
    token, secret, url = args['tokens']
    n = mongo.db.users.update({'user': username},
                              {'$set': {'discogs_info':
                                            {'token': token,
                                            'secret': secret}}})
    form = DiscogsValidationForm()
    if request.method == 'POST':
        oath_code = form.code.data
        n = mongo.db.users.update({'user': username},
                                  {'$set': {'discogs_info.oauth_code': oath_code}})
        return redirect(url_for('collection', username=username))
    return render_template('discogs_signup.html', url=url, form=form)

@app.route('/add_record/', methods=['GET', 'POST'])
@login_required
def add_record():
    args = dict(request.args)
    username = args['username'][0]
    form = AddRecordForm()
    if request.method == 'POST':
        discogs_id = int(form.discogs_id.data)
        if mongo.db.users.find_one({'user': username,
                                    'records': {'$in': [discogs_id]}}) is not None:
            flash('Album already in collection')
            # TODO: returns not found right now
            return redirect(render_template('collection.html',
                                            username=username,
                                            user=mongo.db.users.find_one({'user': username})))
        else:
            n = mongo.db.users.update({'user': username}, {'$addToSet': {'records': discogs_id}})
            record = mongo.db.records.find_one({'_id': discogs_id})
            if record is None:
                album = dclient.release(discogs_id)
                try:
                    n = mongo.db.records.insert_one({'_id': discogs_id,
                                                 'year': int(album.year),
                                                 'title': album.title,
                                                 'artists': [i.name for i in album.artists]})
                except:
                    print(sys.exc_info()[:2])
                print(n)
            return redirect(url_for('collection', username=username,
                                    user=mongo.db.users.find_one({'user': username})))



    return render_template('add_record.html', form=form)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')