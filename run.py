import os
from app import create_app


# app = create_app(os.environ.get('FLASK_CONFIG'))
app = create_app('production')


if app.config.get('RUN_LOCAL'):
    app.run(port=8010)