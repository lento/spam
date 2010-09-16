The *Spark Project & Asset Manager* is a web application originally developed at
[Spark Digital Entertainment](http://www.sparkde.com) to help manage the
production workflow of a 3d animation or VFX pipeline


Installation and Setup of a development environment for SPAM
============================================================

Create a directory where to install SPAM

    $ mkdir ~/spam_development
    

Move to the newly created directory

    $ cd ~/spam_development
    

Create a virtual environment

    $ virtualenv --no-site-packages spamenv


Activate the virtual environment

    $ source spamenv/bin/activate


Clone SPAM repository    

    $ git clone http://github.com/lento/spam.git


Move to the newly created spam source directory

    $ cd spam


Install all requirements, create egginfo and install in the virtualenv in
*develop* mode

    $ python setup.py develop -i http://lorenzopierfederici.net/download/spam/index/simple
    

Edit the configuration file *development.ini* for your environment


Setup the application (this setup a database and creates data directories)

    $ paster setup-app --name=SPAM development.ini


Allow the virtualenv to access locally installed packages (needed for
gstreamer-python)

    $ rm ../spamenv/lib/python2.6/no-global-site-packages.txt


Serve SPAM through a paste server

    $ paster serve --reload development.ini


Access spam from a web-browser

    http://localhost:8080
    

Log-in as:

    User name:  admin
    Password:   none


Enjoy :)
