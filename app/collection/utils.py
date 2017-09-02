from flask import redirect, url_for, flash
from app.models import User, UserRecord, Record

import sys
import datetime

import discogs_client
import requests
from bson import Binary

def add_album(discogs_id, form, dclient, username, user, from_sequence=False):
    if User.objects(user=username, records__id=discogs_id).first() is not None:
        flash('Album already in collection')
        if not from_sequence:
            return redirect(url_for('collection.collection_page', username=username, user=user))
    else:
        user_record = UserRecord(id=discogs_id)
        n = User.objects.get(user=username).update(add_to_set__records=user_record)

        record = Record.objects(_id=discogs_id).first()

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
                print(discogs_id)
                if not from_sequence:
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

                record = Record(_id=discogs_id,
                                year=int(album.year),
                                title=album.title,
                                artists=[i.name for i in artists],
                                tracks=[i.title for i in tracklist],
                                genres=[i for i in genres],
                                styles=styles,
                                image_binary=image_binary,
                                track_data=[i.data for i in tracklist],
                                artist_id=artist_id)
                record.save()
            except:
                print(sys.exc_info()[:2])
        print('Added: ', discogs_id)
