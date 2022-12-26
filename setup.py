from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='cricheroes',
    version='1.0.7',
    packages=['cricheroes'],
    install_requires=['beautifulsoup4', 'python-dateutil', 'selenium'],
    url='https://github.com/pupattan/cricheroes',
    license='MIT',
    author='pattap',
    author_email='pulak.pattanayak@gmail.com',
    description='Python APIs to fetch and store team data from cricheroes.in',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
