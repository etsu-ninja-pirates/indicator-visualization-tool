# README #

A toy project for learning Django and collaborative Git and Jira and stuff

## How do I get set up? ##

### System Requirements ###

1. Install Python 3
2. Install pip ([howto](pip))
3. Using pip, install virtualenvwrapper ([windows](vew-win), [general](vew))

[pip]: https://pip.pypa.io/en/stable/installing/
[vew]: https://virtualenvwrapper.readthedocs.io/en/latest/install.html#installation
[vew-win]: https://virtualenvwrapper.readthedocs.io/en/latest/install.html#windows-command-prompt

### First-time project setup ###

1. Clone this repository
2. Create a virtual python environment for working on the project, e.g. `mkvirtualenv django-sfs`
3. After making sure your virtual environment is active, change into the project directory and use pip to install dependencies: `pip install -r requirements.txt`
4. Populate your local sqlite database with `python manage.py migrate`

* * * * * *

## TODO ##

* Configuration
* Other Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines
