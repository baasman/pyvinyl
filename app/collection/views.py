import math
import pandas as pd

from flask import current_app as capp
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.utils.data_viz import get_items, get_most_common_genres, convert_df_to_items_and_sort
from app.utils.images import upload_image
from app.utils.scrobbler import scrobble_album, update_stats
from app import mongo
from app.utils.api_cons import create_discogs_client, create_lastfm_client
from app.utils.scrape_collection import get_all_ids
from . import collection
from .utils import add_album
from .forms import AddRecordForm, ScrobbleForm, AddTagForm, DiscogsValidationForm, DeleteForm
from .tables import CollectionTable



@collection.route('/u/<username>/collection/')
@collection.route('/u/<username>/collection/p/<int:page>')
@login_required
def collection_page(username, page=0):

    ALBUMS_PER_PAGE = request.args.get('albums_per_page')
    if not ALBUMS_PER_PAGE:
        ALBUMS_PER_PAGE = 10
    else:
        ALBUMS_PER_PAGE = int(ALBUMS_PER_PAGE)

    dclient = create_discogs_client(capp.config)
    user = mongo.db.users.find_one({'user': username})
    df = get_items(user, for_table=False)
    df = pd.DataFrame(df, columns=['Title', 'Artist', 'Year', 'Genre', 'Style',
                                        'TimesPlayed', 'DateAdded'])
    items = convert_df_to_items_and_sort(df, user=user, sort_on='DateAdded')
    n_pages = list(range(math.ceil(len(items) / ALBUMS_PER_PAGE)))

    sub_items = items[ALBUMS_PER_PAGE * page : (page * ALBUMS_PER_PAGE) + ALBUMS_PER_PAGE]

    if len(sub_items) > 0:
        table = CollectionTable(sub_items)
    else:
        table = None
    return render_template('collection/collection.html', username=username, user=user,
                           client=dclient, table=table, pages=n_pages)

@collection.route('/u/<string:username>/explore', methods=['GET', 'POST'])
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
            add_album(discogs_id, form, dclient, username, user)
        elif form.collection_link.data:
            all_ids = get_all_ids(form.collection_link.data)
            for discogs_id in all_ids[:4]:
                add_album(discogs_id, form, dclient, username, user, from_sequence=True)
        return redirect(url_for('collection.collection_page', username=username,
                                user=user))
    return render_template('collection/add_record.html', form=form)


@collection.route('/u/<string:username>/album/<int:album_id>', methods=['GET', 'POST', 'DELETE'])
def album_page(username, album_id):
    user = mongo.db.users.find_one({'user': username})
    record = mongo.db.records.find_one({'_id': album_id})
    scrobble_form = ScrobbleForm()
    tag_form = AddTagForm()
    delete_form = DeleteForm()

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
                    exists = list(mongo.db.users.aggregate([
                        {'$unwind': '$tags'},
                        {'$match': {'tags.tag': tags, 'tags.id': album_id}}
                    ]))
                    if not exists:
                        n1 = mongo.db.users.update({'user': username},
                                                   {'$push': {'tags': {'tag': tag,
                                                                       'id': album_id}}})
                    else:
                        flash('tag already exists for this album', category='Warning')
            else:
                exists = list(mongo.db.users.aggregate([
                    {'$unwind': '$tags'},
                    {'$match': {'tags.tag': tags, 'tags.id': album_id}}
                ]))
                if not exists:
                    n1 = mongo.db.users.update({'user': username},
                                               {'$push': {'tags': {'tag': tags,
                                                               'id': album_id}}})
                else:
                    flash('tag already exists for this album', category='Warning')

            return render_template('collection/album_page.html', record=record, filename=fname,
                                   scrobble_form=scrobble_form, total_user_plays=total_user_plays,
                                   tag_form=tag_form, delete_form=delete_form)

        elif scrobble_form.validate_on_submit():
            dt = scrobble_form.play_date.data
            has_time = record['track_data'][0]['duration'] != ''
            if scrobble_form.submit.data:
                try:
                    lfclient = create_lastfm_client(capp.config, user)
                except:
                    redirect(url_for('auth.lastfm_setup', username=username))
                scrobble_album(lfclient, record, dt)
                update_stats(username, album_id, dt)
            elif scrobble_form.just_record_submit.data:
                update_stats(username, album_id, dt)
            flash('Album recorded!', category='Success')
            return render_template('collection/album_page.html', record=record, filename=fname,
                                   has_time=has_time, scrobble_form=scrobble_form,
                                   total_user_plays=total_user_plays, tag_form=tag_form,
                                   delete_form=delete_form)

        elif request.method == 'POST' and delete_form.delete.data and delete_form.validate_on_submit():

            try:
                mongo.db.records.delete_one({'_id': album_id})
                mongo.db.users.update({'user': username},
                                      {'$pull': {'records': {'id': album_id}}})
                mongo.db.users.update({'user': username},
                                      {'$pull': {'tags': {'id': album_id}}})
            except:
                pass
            return redirect(url_for('collection.collection_page', username=username))

    return render_template('collection/album_page.html', record=record, filename=fname,
                           scrobble_form=scrobble_form, total_user_plays=total_user_plays,
                           tag_form=tag_form, delete_form=delete_form)

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
    if request.method == 'POST' and form.validate_on_submit():
        oath_code = form.code.data
        access_token, access_secret = dclient.get_access_token(oath_code)
        n = mongo.db.users.update({'user': username},
                                  {'$set': {'discogs_info.oauth_code': oath_code,
                                            'discogs_info.access_token': access_token,
                                            'discogs_info.access_secret': access_secret}})
        return redirect(url_for('collection.collection_page', username=username))
    return render_template('collection/discogs_signup.html', url=url, form=form)

