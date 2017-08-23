from werkzeug.contrib.profiler import ProfilerMiddleware
from app import create_app

app = create_app('development')
app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

if app.config.get('RUN_LOCAL'):
    app.run(port=8010)