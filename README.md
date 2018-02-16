# iot.things.srv


Add user for iot servers:

    sudo useradd -s /usr/sbin/nologin -r -M srv-user


Add Python3 virtual env:

    sudo apt-get install python3-virtualenv


Add directory for mongo backups:

    sudo mkdir -p /var/backups/mongodb
    sudo chgrp srv-user /var/backups/mongodb
    sudo chmod g+w /var/backups/mongodb


Setup global.conf:

    sudo mkdir -p /etc/iot.things.srv/
    sudo cp etc/iot.things.srv/global.conf /etc/iot.things.srv/
    # edit global.cnf with your credentials
    sudo vim /etc/iot.things.srv/global.conf
    # create ssl key
    sudo sh -c 'openssl genrsa 1024 > /etc/iot.things.srv/ssl.key'
    sudo sh -c 'openssl req -new -x509 -nodes -sha1 -days 365 -key /etc/iot.things.srv/ssl.key > /etc/iot.things.srv/ssl.cert'


Setup gunicorn :

    sudo apt-get -t jessie-backports install gunicorn3


Setup mongo :

    sudo apt-get install mongodb


Setup supervisor :

    sudo apt-get install supervisor
    sudo cp etc/supervisor/conf.d/* /etc/supervisor/conf.d/
    sudo supervisorctl update
