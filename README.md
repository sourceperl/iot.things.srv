# iot.things.srv


Add user for iot servers:

    sudo useradd -s /usr/sbin/nologin -r -M srv-user


Add directory for mongo backups:

    sudo mkdir -p /var/backups/mongodb
    sudo chgrp srv-user /var/backups/mongodb
    sudo chmod g+w /var/backups/mongodb


Setup global.conf:

    sudo mkdir -p /etc/iot.things.srv/
    sudo cp etc/iot.things.srv/global.conf /etc/iot.things.srv/
    # edit global.cnf with your credentials
    sudo vim /etc/iot.things.srv/global.conf


Setup mongo :

    sudo apt-get install mongodb


Setup supervisor :

    sudo apt-get install supervisor
    sudo cp etc/supervisor/conf.d/* /etc/supervisor/conf.d/
    sudo supervisorctl update
