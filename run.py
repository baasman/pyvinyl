import os
from app import create_app
from app import login_manager
from app.models import User
from mongoengine.errors import DoesNotExist

app = create_app(os.environ.get('FLASK_CONFIG'))


# TODO: MOVE THIS FUNCTION ELSEWHERE
@login_manager.user_loader
def load_user(user):
    try:
        user = User.objects.get(user=user)
        return user
    except DoesNotExist:
        return None


if app.config.get('RUN_LOCAL'):
    app.run(port=8010)