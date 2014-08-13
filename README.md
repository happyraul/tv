Snow Day
==========
### Setup
1. Configure settings

        $ python configure.py
        DATABASE_PASSWORD [tv_password] : 
        DATABASE_USER [tv_user] : 
        DEV_DATABASE_PASSWORD [tv_password] : 
        DEV_DATABASE_USER [tv_user] : 
        MAIL_PASSWORD [example_password] : 
        MAIL_USERNAME [user@example.com] : 
        SECRET_KEY [changeme] : 
        SNOW_DAY_ADMIN [admin] : 
        TEST_DATABASE_PASSWORD [tv_password] : 
        TEST_DATABASE_USER [tv_user] :

2. Install server packages

        $ sudo apt-get install postgresql python-dev libpq-dev python-pip

3. Install python dependencies

        $ pip install -r requirements.txt

4. Set up PostgreSQL databases
        
        $ sudo -u postgres createuser $DEV_DATABASE_USER
        $ sudo -u postgres psql postgres
        # \password $DEV_DATABASE_USER
        # create database tv_dev owner $DEV_DATABASE_USER;

5. Configure PostgreSQL

        $ sudo vi /etc/postgresql/9.3/main/pg_hba.conf

    Add line:

        local   tv_dev,tv_test,tv   $DEV_DATABASE_USER    md5

6. Initialize data

        $ python manage.py db upgrade

7. Start server

        $ python manage.py runserver
        
