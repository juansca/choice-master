# NyP

## installation and deploy

### make virtual environment and install dependendencies

- install and configure:
    - [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
    - [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/install.html)
- make virtualenv with `mkvirtualenv --python=$(which python3) ingsoft`
- install required python packages: `pip install -r requirements`

### configure

- provide local settings: `cp choice_master/local_settings.py.template choice_master/local_settings.py && nano choice_master/local_settings.py`
- synchronize database: `python manage.py migrate`
- create super-user: `python manage.py createsuperuser`

### `allauth` configuration
- we are using [django-allauth](http://django-allauth.readthedocs.io/)
- run server `python manage.py runserver`
- go to admin page at http://127.0.0.1:8000/admin and log in as superuser
- create a site and put its id on settings.SITE_ID (probably it receives id = 2)
- For each OAuth based provider, add a Social App (socialaccount app).
- Fill in the site and the OAuth app credentials obtained from the provider.
- For example, if you want to set up login using google, read [this](http://django-allauth.readthedocs.io/en/latest/providers.html#google)

