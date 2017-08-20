import discogs_client
import pylast

def create_discogs_client(config):
    user_agent = 'discogs_pyvy/1.0'
    dclient = discogs_client.Client(user_agent)
    dclient.set_consumer_key(config['DISCOGS_CONSUMER_KEY'], config['DISCOGS_CONSUMER_SECRET'])
    dclient.set_token(config['ACCESS_TOKEN'], config['ACCESS_SECRET'])
    return dclient

def create_lastfm_client(config, user):
    if user['lfm_is_authenticated']:
        lastfm_client = pylast.LastFMNetwork(api_key=config['LASTFM_API_KEY'],
                                             api_secret=config['LASTFM_API_SECRET'],
                                             username=user['lastfm_username'],
                                             password_hash=user['lastfm_password'],
                                             session_key=user['lfm_session_key'])
    else:
        raise Exception
    return lastfm_client