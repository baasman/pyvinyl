from flask import render_template

from . import errors


@errors.errorhandler(404)
def not_found_error(error):
    print(error)
    return render_template('404.html'), 404


@errors.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500