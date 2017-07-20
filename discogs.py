import discogs_client
from app import app
import oauth2 as oa

def test_discogs():
    user_agent = 'discogs_pyvy/1.0'
    dclient = discogs_client.Client(user_agent)
    dclient.set_consumer_key(app.config['DISCOGS_CONSUMER_KEY'], app.config['DISCOGS_CONSUMER_SECRET'])
    token, secret, url = dclient.get_authorize_url()
    oath_code = 'NdNMAWtBvJ'
    access_token, access_secret = dclient.get_access_token(oath_code)
    user = dclient.identity()
    search_results = dclient.search('Tim', type='release',
                                    artist='The Replacements')
    release = search_results[0]

def get_collection():
    # examples
    secret = 'IPxLpjVdLqjjorRTiqdqlhZOTvxBgHHGQPQUizXO'
    token = 'bITlsDMmfPXASMoERpYqvaWbAbRjnaUQkZebGDEQ'
    oauth_code = 'QslAnoqQLn'

    user_agent = 'discogs_pyvy/1.0'
    dclient = discogs_client.Client(user_agent)
    dclient.set_consumer_key(app.config['DISCOGS_CONSUMER_KEY'], app.config['DISCOGS_CONSUMER_SECRET'])

    access_token, access_secret = dclient.get_access_token(oauth_code)