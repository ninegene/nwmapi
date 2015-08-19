
## Initial Setup
```
cd nwmapi
virtualenv env
source env/bin/activate.fish
python setup develop
bin/initialize_nwmdb development.ini
```

## Run
```
paster serve development.ini --reload
```

## Reading
* http://pythonpaste.org/script/
* http://pythonpaste.org/deploy/#egg-uris
* http://docs.pylonsproject.org/projects/waitress/en/latest/
* https://lionfacelemonface.wordpress.com/2011/03/30/wsgi-and-paste-deploy-the-bare-necessities/
