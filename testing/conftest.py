import pytest

import datetime
import random

from faker import Faker

from app import create_app, mongo

def add_non_lfm_user(faker):
    username = faker.user_name()
    lastfm_username = faker.user_name()
    password = faker.sha1(raw_output=False)
    passwordfm = faker.sha1(raw_output=False)

    record_list = [{'id': 10276599, 'date_added': datetime.datetime.now(),
                    'count': random.choice(list(range(20)))},
                   {'id': 4418602, 'date_added': datetime.datetime.now(),
                    'count': random.choice(list(range(20)))},
                   {'id': 742901, 'date_added': datetime.datetime.now(),
                    'count': random.choice(list(range(20)))},
                   {'id': 8888892, 'date_added': datetime.datetime.now(),
                    'count': random.choice(list(range(20)))},
                   {'id': 9687733, 'date_added': datetime.datetime.now(),
                    'count': random.choice(list(range(20)))},
                   {'id': 2319571, 'date_added': datetime.datetime.now(),
                    'count': random.choice(list(range(20)))},
                   {'id': 6549215, 'date_added': datetime.datetime.now(),
                    'count': random.choice(list(range(20)))},
                   {'id': 6118921, 'date_added': datetime.datetime.now(),
                    'count': random.choice(list(range(20)))},
                   {'id': 2062878, 'date_added': datetime.datetime.now(),
                    'count': random.choice(list(range(20)))},
                   ]

    email = faker.safe_email()

    n = mongo.db.users.insert_one({'user': username,
                                   'email': email,
                                   'password_hash': password,
                                   'lastfm_username': lastfm_username,
                                   'lastfm_password': passwordfm,
                                   'records': random.sample(record_list, random.randint(1, len(record_list))),
                                   'tmp_files': [],
                                   'discogs_info': {'oath_token': None,
                                                    'token': None,
                                                    'secret': None}})
    return username


@pytest.fixture
def app():
    return create_app('testing')

@pytest.fixture
def mongodb():
    fake = Faker()
    for _ in range(100):
        add_non_lfm_user(fake)
    yield mongo
    print('Tear down')
    mongo.db.users.remove({})
