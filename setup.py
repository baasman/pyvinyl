from setuptools import setup, find_packages

requirements = [
    'Flask>=0.11.1',
    'flask_login>=0.4.0',
    'flask_bootstrap>=3.3.7.1',
    'flask_pymongo>=0.5.1',
    'flask_wtf>=0.14.2',
    'flask_table>=0.4.1',
    'werkzeug>=0.11.10',
    'pandas>=0.20.1',
    'discogs_client>=2.2.1',
    'pylast>=1.5.4',
    'pymongo>=3.5.0',
    'wtforms>=2.1'
]

setup(
    name='app',
    version='0.1',
    url='https://github.com/baasman/pyvinyl',
    author='Boudewijn Aasman',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    description=('A flask app to manage your record collection'),
    install_requires=requirements
)