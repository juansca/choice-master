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
- start enjoing ChoiceMaster on your browser: `python manage.py runserver`


### Pasos a seguir luego de hacer un pull en limpio.

rm db.sqlite3;

cp choice_master/local_settings.py.template choice_master/local_settings.py;

workon ingsoft;

python manage.py migrate;

python manage.py createsuperuser;

python manage.py runserver;

- Ir a http://127.0.0.1:8000/admin e ingresar como superusuario

- modificar el sitio example.com:
  Nombre de dominio: 127.0.0.1:8000
  Nombre para visualizar: Choice Master

- Mientras se lo modifica mirar la url.
  Tiene que ser de la forma: http://localhost:8000/admin/sites/site/n/change/
  Donde n es un número. Ese número es el SITE_ID. Ir a configure.py en el
  directorio choice_master/choice_master y modificar ese valor a n
  (probablemente n sea 3).
- Agregar una social application de google con los siguientes datos (sin comillas):

Nombre: "Google"

Client id: "576052722164-tdkaff0p8ocuj3698nf7v069q6lplrt7.apps.googleusercontent.com"

Secret Key: "B76ysRJpfdQOHyfBiPK_xvxK"

Agregar el único sitio a la lista de sitios seleccionados.

- Agregar otra social application de Github con los siguientes datos (sin comillas):

Nombre: "Github"

Client id: "6e895d85a935398a924e"

Secret Key: "8b0e4e46b7283e6478351aeb042a2690b5aea3f4"

Agregar el único sitio a la lista de sitios seleccionados.


