# NyP

## install and deploy

### make virtual environment and install dependendencies

- install and configure:
    - [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
    - [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/install.html)
- make virtualenv with `mkvirtualenv --python=$(which python3) ingsoft`
- install required python packages: `pip install -r requirements`

### configure and run project

- provide local settings: `cp choice_master/local_settings.py.template choice_master/local_settings.py`
- synchronize database: `python manage.py migrate`
- load initial data: `python manage.py loaddata chm/fixtures/initial_data.json`
- start enjoing ChoiceMaster on your browser: `python manage.py runserver`

### Default superuser
Username : "admin"
Password : "adminadmin"
