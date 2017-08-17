import pytest

@pytest.mark.usefixtures('mongodb', 'app')
class TestDatabase():

    def test_config(self, app):
        with app.test_client() as client:
            assert client.application.config['MONGO2_DBNAME'] == 'test'

    def test_mongo(self, app, mongodb):
        with app.app_context():
            assert mongodb.db.name == 'test'
            assert mongodb.db.users.count() > 0