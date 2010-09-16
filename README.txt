This file describe the spam application.

Installation and Setup
======================

Create a directory where you want to install SPAM, egg.
    $ mkdir ~/spam_directory
    
Move to newly created directory
    $ cd ~/spam_directory
    
Create new virtual environment
    $ virtualenv --no-site-packages spamenv

Activate virtual environment
    $ source spamenv/bin/activate

Clone SPAM repository    
    $ git clone http://github.com/lento/spam.git

Move to newly created directory with spam source
    $ cd spam

Install all requires
    $ python setup.py develop -i http://lorenzopierfederici.net/download/spam/index/simple
    
First time setup - this step is required for installation non for update
    $ paster setup-app --name=SPAM development.ini

Open access to local installed tools
    $ rm ../spamenv/lib/python2.6/no-global-site-packages.txt

Start SPAM server
    $ paster serve --reload development.ini

Access spam - insert in web-browser
    http://localhost:8080
    
For log-in use
    User name:  admin
    Password:   none
             * advice: change admin password after first log-in

Enjoy.
