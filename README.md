
## Initial Setup
```
# for bcrypt
sudo apt-get install build-essential libffi-dev python-dev

cd nwmapi
virtualenv env
source env/bin/activate.fish
pip install cython
pip install falcon
pip install PasteDeploy
pip install PasteScript
pip install waitress
pip install sqlalchemy
pip install bcrypt
pip install python-dateutil
python setup develop
bin/initialize_nwmdb development.ini
```

## Run
```
$ source venv/bin/activate.fish
$ paster serve development.ini --reload
```


## alembic

### Install
```
$ source venv/bin/activate.fish
$ pip install alembic
$ alembic init alembic
```

### Import Error with --authogenerate
Make nwaapi as an application with "python setup.py develop"
```
$ source venv/bin/activate.fish
$ python setup.py develop
```
See: https://bitbucket.org/zzzeek/alembic/issues/87/importerror-with-autogenerate

### first revision
```
$ alembic revision --autogenerate -m "Remove user fullname and add firstname, middlename, lastname"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added column 'user.firstname'
INFO  [alembic.autogenerate.compare] Detected added column 'user.lastname'
INFO  [alembic.autogenerate.compare] Detected added column 'user.middlename'
INFO  [alembic.autogenerate.compare] Detected NOT NULL on column 'user.email'
INFO  [alembic.autogenerate.compare] Detected NOT NULL on column 'user.username'
INFO  [alembic.autogenerate.compare] Detected removed column 'user.fullname'
  Generating /home/aung/Projects/nwmapi/alembic/versions/42949c3d5ac2_remove_user_fullname_and_add_firstname_.py ... done
  
$ alembic upgrade head
```

### Re-initialize db for sqlite
Cannot drop column in sqlite. Use delete nwmdb-dev.sqlite and use initializedb.py
```
$ rm nwmdb-dev.sqlite
$ initialize_nwmdb development.ini
```

### Install postgresql driver

```
$ sudo apt-get install python-dev libpq-dev
$ pip install psycopg2
```

### Re-initialize db for postgresql
Drop and create nwmdb
```
$ sudo -i -u postgres dropdb nwmdb
 
$ sudo -i -u postgres createdb -O nwm nwmdb

$ cd nwmapi
$ source venv/bin/activate.fish 
$ initialize_nwmdb development.ini
```

### What does Autogenerate Detect (and what does it not detect?)
The vast majority of user issues with Alembic centers on the topic of what kinds of changes autogenerate can and cannot detect reliably, as well as how it renders Python code for what it does detect. it is critical to note that autogenerate is not intended to be perfect. It is always necessary to manually review and correct the candidate migrations that autogenererate produces. The feature is getting more and more comprehensive and error-free as releases continue, but one should take note of the current limitations.

Autogenerate will detect:

* Table additions, removals.
* Column additions, removals.
* Change of nullable status on columns.
* Basic changes in indexes and explcitly-named unique constraints
* New in version 0.6.1: Support for autogenerate of indexes and unique constraints.

Basic changes in foreign key constraints
New in version 0.7.1: Support for autogenerate of foreign key constraints.

Autogenerate can optionally detect:

* Change of column type. This will occur if you set the EnvironmentContext.configure.compare_type parameter to True, or to a custom callable function. The feature works well in most cases, but is off by default so that it can be tested on the target schema first. It can also be customized by passing a callable here; see the section Comparing Types for details.
* Change of server default. This will occur if you set the EnvironmentContext.configure.compare_server_default parameter to True, or to a custom callable function. This feature works well for simple cases but cannot always produce accurate results. The Postgresql backend will actually invoke the “detected” and “metadata” values against the database to determine equivalence. The feature is off by default so that it can be tested on the target schema first. Like type comparison, it can also be customized by passing a callable; see the function’s documentation for details.

Autogenerate can not detect:

* Changes of table name. These will come out as an add/drop of two different tables, and should be hand-edited into a name change instead.
* Changes of column name. Like table name changes, these are detected as a column add/drop pair, which is not at all the same as a name change.
* Anonymously named constraints. Give your constraints a name, e.g. UniqueConstraint('col1', 'col2', name="my_name"). See the section The Importance of Naming Constraints for background on how to configure automatic naming schemes for constraints.
* Special SQLAlchemy types such as Enum when generated on a backend which doesn’t support ENUM directly - this because the representation of such a type in the non-supporting database, i.e. a CHAR+ CHECK constraint, could be any kind of CHAR+CHECK. For SQLAlchemy to determine that this is actually an ENUM would only be a guess, something that’s generally a bad idea. To implement your own “guessing” function here, use the sqlalchemy.events.DDLEvents.column_reflect() event to detect when a CHAR (or whatever the target type is) is reflected, and change it to an ENUM (or whatever type is desired) if it is known that that’s the intent of the type. The sqlalchemy.events.DDLEvents.after_parent_attach() can be used within the autogenerate process to intercept and un-attach unwanted CHECK constraints.

Autogenerate can’t currently, but will eventually detect:

* Some free-standing constraint additions and removals, like CHECK, PRIMARY KEY - these are not fully implemented.
* Sequence additions, removals - not yet implemented.


## Reading
* http://pythonpaste.org/script/
* http://pythonpaste.org/deploy/#egg-uris
* http://docs.pylonsproject.org/projects/waitress/en/latest/
* https://lionfacelemonface.wordpress.com/2011/03/30/wsgi-and-paste-deploy-the-bare-necessities/
