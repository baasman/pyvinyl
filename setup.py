from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='app',
    version='0.1',
    url='https://github.com/baasman/pyvinyl',
    author='Boudewijn Aasman',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    description=('A flask app to manage your record collection'),
    install_requires=required
)