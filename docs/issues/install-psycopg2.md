## Require libpq-dev to install psycopg2

```console
(venv)~/P/nwmapi$ pip install psycopg2
    Error: You need to install postgresql-server-dev-X.Y for building a server-side extension or libpq-dev for building a client-side application.
    ----------------------------------------
Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-build-s99tla/psycopg2

(venv)~/P/nwmapi$ sudo apt-get install python-dev libpq-dev
```

