# Initial Setup

## Ubuntu with Python 2
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
pip install alembic

python setup develop
bin/initialize_nwmdb development.ini
```

## Mac with Python 3
```

brew update
brew install python3
brew install postgresql

mkdir -p ~/Library/LaunchAgents
ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents

launchctl load ~/Library/LaunchAgents/homebrew.mxcl.postgresql.plist

initdb /usr/local/var/postgres -E utf8

gem install lunchy
lunchy start postgresql

createdb nwmdb
createuser nwm

cd nwmapi
pyvenv venv
source venv/bin/activate.fish

pip install cython
pip install falcon
pip install six
pip install PasteDeploy
pip install PasteScript
pip install waitress
pip install sqlalchemy
pip install bcrypt
pip install python-dateutil
pip install alembic
pip install psycopg2

```

* https://www.codefellows.org/blog/three-battle-tested-ways-to-install-postgresql

### Problem running `psql`
```
$ psql
psql: could not connect to server: No such file or directory
	Is the server running locally and accepting
	connections on Unix domain socket "/tmp/.s.PGSQL.5432"?
```

```
lunchy stop postgresql
sudo rm -rf /usr/local/var/postgres/
initdb /usr/local/var/postgres -E utf8
lunchy start postgresql
```

```
$ psql
psql: FATAL:  database "aung" does not exist

~$ createdb (whoami)

~$ psql
psql (9.5.0)
Type "help" for help.

aung=#
```

* http://stackoverflow.com/questions/13410686/postgres-could-not-connect-to-server
