import pytest

from flask import url_for


@pytest.mark.usefixtures('app')
class TestAuth():

    def test_views(self, app):
        with app.test_client() as client:
            assert client.get(url_for('auth.login')).status_code == 200
            assert client.get(url_for('auth.register')).status_code == 200
            assert client.get(url_for('home.homepage')).status_code == 200


