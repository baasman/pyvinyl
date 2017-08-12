import datetime
import sys

import discogs_client
import pandas as pd
import requests
from bson import Binary
from flask import current_app as capp
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required

from app.utils.data_viz import get_items, get_most_common_genres
from app.utils.images import upload_image
from app.utils.scrobbler import scrobble_album, update_stats
from app import mongo, login_manager
from app.utils.api_cons import create_discogs_client, create_lastfm_client
from . import collection
from .forms import AddRecordForm, ScrobbleForm, AddTagForm, DiscogsValidationForm
from .tables import CollectionTable


# TODO: dont forget login_required

@collection.route('/collection/<username>')
@login_required
def collection_page(username):
    dclient = create_discogs_client(capp.config)
    sort = request.args.get('sort')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    user = mongo.db.users.find_one({'user': username})
    items = get_items(user, for_table=True)

    if len(items) > 0:
        table = CollectionTable(items)
    else:
        table = None
    return render_template('collection/collection.html', username=username, user=user,
                           client=dclient, table=table)

@collection.route('/<string:username>/explore', methods=['GET', 'POST'])
@login_required
def explore_collection(username):
    user = mongo.db.users.find_one({'user': username})
    df_list = get_items(user, for_table=False, add_breakpoints=True)
    df = pd.DataFrame(df_list, columns=['Title', 'Artist', 'Year', 'Genre', 'Style',
                                        'TimesPlayed', 'DateAdded'])
    genres = get_most_common_genres(df)

    all_tags = list(mongo.db.users.aggregate([
        {'$match': {'user': username}},
        {'$unwind': '$tags'},
        {'$project': {'tags': 1}},
        {'$group': {'_id': '$tags.tag', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]))

    top_albums = df.sort_values('TimesPlayed', ascending=False)[['Title', 'TimesPlayed']].head(6)
    records = []
    for title in top_albums.Title.values:
        records.append(mongo.db.records.find_one({'title': title}))

    images_to_display = []
    for record in records:
        fname = upload_image(record, username)
        n_plays_by_user = top_albums.loc[top_albums.Title == record['title'], 'TimesPlayed'].values[0]
        images_to_display.append((fname, record['_id'], n_plays_by_user))

    return render_template('collection/explore_collection.html', filename=fname,
                           images_to_display=images_to_display, user=user,
                           most_common_genres=genres[:6],
                           most_common_tags=all_tags[:6])

@collection.route('/add_record/', methods=['GET', 'POST'])
@login_required
def add_record():

    dclient = create_discogs_client(capp.config)

    args = dict(request.args)
    username = args['username'][0]

    user = mongo.db.users.find_one({'user': username})
    form = AddRecordForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.discogs_id.data:
            discogs_id = int(form.discogs_id.data)
        else:
            discogs_id = int(form.discogs_master_id.data)
        if mongo.db.users.find_one({'user': username,
                                    'records': {'$in': [discogs_id]}}) is not None:
            flash('Album already in collection')
            return redirect(url_for('collection', username=username, user=user))
        else:
            n = mongo.db.users.update({'user': username}, {'$addToSet': {'records':
                                                                             {'id': discogs_id,
                                                                              'count': 0,
                                                                              'date_added': datetime.datetime.now()}}})
            record = mongo.db.records.find_one({'_id': discogs_id})
            if record is None:
                album = dclient.release(discogs_id)
                try:
                    tracklist = album.tracklist
                    artists = album.artists
                    genres = album.genres
                    styles = album.styles
                    image = album.images[0]
                except discogs_client.exceptions.HTTPError:
                    flash('Could not find release on discogs. Double check the release id')
                    return redirect(url_for('add_record', username=username))
                try:
                    try:
                        image_bytes = requests.get(image['resource_url']).content
                        image_binary = Binary(image_bytes)
                    except:
                        image_binary = 'default_image'
                    artist_id = artists[0].id

                    if not styles:
                        styles = ''
                    else:
                        styles = [i for i in styles]

                    n = mongo.db.records.insert_one({'_id': discogs_id,
                                                     'year': int(album.year),
                                                     'title': album.title,
                                                     'artists': [i.name for i in artists],
                                                     'tracks': [i.title for i in tracklist],
                                                     'genres': [i for i in genres],
                                                     'styles': styles,
                                                     'image': image,
                                                     'image_binary': image_binary,
                                                     'track_data': [i.data for i in tracklist],
                                                     'total_plays': 0,
                                                     'plays': [],
                                                     'artist_id': artist_id})
                except:
                    print(sys.exc_info()[:2])
            return redirect(url_for('collection.collection_page', username=username,
                                    user=mongo.db.users.find_one({'user': username})))
    return render_template('collection/add_record.html', form=form)

@collection.route('/user/<string:username>/album/<int:album_id>', methods=['GET', 'POST'])
def album_page(username, album_id):
    user = mongo.db.users.find_one({'user': username})
    record = mongo.db.records.find_one({'_id': album_id})
    scrobble_form = ScrobbleForm()
    tag_form = AddTagForm()

    total_user_plays = mongo.db.users.find_one(
        {'user': username, 'records.id': album_id},
        {'_id': 0, 'records.$': 1}
    )

    if total_user_plays:
        total_user_plays = total_user_plays['records'][0]['count']
    else:
        total_user_plays = 0

    fname = upload_image(record, username)

    if request.method == 'POST':

        # TODO: scrobble form should not be called if tag form field is empty
        if tag_form.submit.data and tag_form.validate_on_submit():
            tags = tag_form.tag.data
            if ',' in tags:
                tags = tags.replace(' ', '')
                tags = tags.split(',')
                for tag in tags:
                    exists = mongo.db.users.find_one({'user': username,
                                                      'tags': {'$elemMatch':
                                                                   {'tags.id': album_id,
                                                                    'tags.tag': tag}}})
                    if not exists:
                        n1 = mongo.db.users.update({'user': username},
                                                   {'$push': {'tags': {'tag': tag,
                                                                       'id': album_id}}})
                    else:
                        print('tag already exists for this album')
            else:
                exists = mongo.db.users.find_one({'user': username,
                                                  'tags': {'$elemMatch':
                                                               {'tags.id': album_id,
                                                                'tags.tag': tags}}})
                if not exists:
                    n1 = mongo.db.users.update({'user': username},
                                               {'$push': {'tags': {'tag': tags,
                                                               'id': album_id}}})
                else:
                    print('tag already exists for this album')

            return render_template('collection/album_page.html', record=record, filename=fname,
                                   scrobble_form=scrobble_form, total_user_plays=total_user_plays,
                                   tag_form=tag_form)

        elif scrobble_form.validate_on_submit():
            dt = scrobble_form.play_date.data
            has_time = record['track_data'][0]['duration'] != ''
            if scrobble_form.submit.data:
                lfclient = create_lastfm_client(capp.config, username, user['lastfm_password'])
                scrobble_album(lfclient, record, dt)
                update_stats(username, album_id, dt)
            elif scrobble_form.just_record_submit.data:
                update_stats(username, album_id, dt)
            return render_template('collection/album_page.html', record=record, filename=fname,
                                   has_time=has_time, scrobble_form=scrobble_form,
                                   total_user_plays=total_user_plays, tag_form=tag_form)

    return render_template('collection/album_page.html', record=record, filename=fname,
                           scrobble_form=scrobble_form, total_user_plays=total_user_plays,
                           tag_form=tag_form)

@collection.route('/discogs_setup/<username>', methods=['GET', 'POST'])
def discogs_setup(username):
    dclient = create_discogs_client(capp.config)
    args = dict(request.args)
    token, secret, url = args['tokens']
    n = mongo.db.users.update({'user': username},
                              {'$set': {'discogs_info':
                                            {'token': token,
                                            'secret': secret}}})
    form = DiscogsValidationForm()
    if request.method == 'POST':
        oath_code = form.code.data
        access_token, access_secret = dclient.get_access_token(oath_code)
        n = mongo.db.users.update({'user': username},
                                  {'$set': {'discogs_info.oauth_code': oath_code,
                                            'discogs_info.access_token': access_token,
                                            'discogs_info.access_secret': access_secret}})
        return redirect(url_for('collection.collection_page', username=username))
    return render_template('collection/discogs_signup.html', url=url, form=form)

