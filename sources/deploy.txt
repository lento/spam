Deploying SPAM
==============

Requirements
------------

* MySQL
* Apache + mod_wsgi


Setup MySQL (on the dbserver)
-----------------------------
set INNODB as default table engine
(add the following line to the [mysqld] section of /etc/my.cnf) ::
    
    default-storage-engine=INNODB

restart mysql ::
 
    service mysqld restart

connect to mysql as root ::
 
    mysql -u root -p
    (enter password)

create a database for SPAM ::
 
    CREATE DATABASE spam;

create a db user for spam on localhost ::
 
    GRANT ALL ON spam.* to 'spamuser'@'localhost' IDENTIFIED BY '<db password>';

(optional) grant spamuser permission to connect from a different host if MySQL
and Apache are not on the same server ::
 
    GRANT ALL ON spam.* to 'spamuser'@'<webserver>' IDENTIFIED BY '<db password>';


Create a virtualenv (on the webserver)
--------------------------------------
::

    mkdir -p /var/www/wsgi/virtualenv
    cd /var/www/wsgi/virtualenv
    virtualenv tg21env


Activate the virtualenv
-----------------------
::

    source /var/www/wsgi/virtualenv/tg21env/bin/activate


Install TurboGears
------------------
::

    easy_install -i http://www.turbogears.org/2.1/downloads/current/index tg.devtools


Install SPAM
------------
::

    mkdir -p /var/www/wsgi/apps
    cd /var/www/wsgi/apps
    (copiare la directory livewidgets/ in /var/www/wsgi/apps)
    cd livewidgets
    python setup.py develop

    cd /var/www/wsgi/apps
    (copiare la directory mrClientMaker/ in /var/www/wsgi/apps)
    cd mrClientMaker
    python setup.py develop

    cd /var/www/wsgi/apps
    (copiare la directory spam/ in /var/www/wsgi/apps)
    cd spam
    python setup.py develop


Create data dirs for SPAM
-------------------------
::

    mkdir -p /var/www/wsgi/data/spam/{data,templates}


Initialize SPAM
---------------
create local configuration files ::
 
    cd /var/www/wsgi/apps/spam
    cp deployment.ini deployment_local.ini
    cp orbited.cfg orbited_local.cfg

update config file with <db password>
(change the following line in /var/www/wsgi/apps/spam/deployment_local.ini,
if Apache and MySQL are not on the same server change `localhost` to
the correct <dbserver> name) ::
   
    sqlalchemy.url=mysql://spamuser:<db password>@localhost:3306/spam

update orbited config file with <webserver>
(change the following line in the [access] section of
/var/www/wsgi/apps/spam/orbited_local.cfg) ::
   
    * -> <webserver>:61613
    
init database ::
 
    paster setup-app --name=SPAM deployment_local.ini


Allow Apache to access the dirs it needs
----------------------------------------
::

    chown -R apache:apache /var/www/wsgi/apps/spam/apache
    chown -R apache:apache /var/www/wsgi/data/spam


Configure apache to serve SPAM
------------------------------
::

    ln -s /var/www/wsgi/apps/spam/apache/spam.conf /etc/httpd/conf.d/


Configure orbited to run at startup
-----------------------------------
(this is just an example, you can use your distribution's init scripts to
manage the orbited deamon) ::
    cat >> /etc/rc.local << EOF

    source /var/www/wsgi/virtualenv/tg21env/bin/activate
    orbited --config /var/www/wsgi/apps/spam/orbited_local.cfg &
    deactivate
    EOF


Start orbited and Apache
------------------------
::

    orbited --config /var/www/wsgi/apps/spam/orbited_local.cfg
    service httpd start

