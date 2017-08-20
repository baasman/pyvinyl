from flask import render_template

class LFMAPIError(Exception):

    def __init__(self, error='auth_error'):
        self.error = error

    def __str__(self):
        return 'LFMAPIError: %s' % self.error


def not_found_error(error):
    print(error)
    return render_template('404.html'), 404


def server_error(error):
    print(error)
    return render_template('500.html'), 500