# BasicFlaskApp
This is a basic flask app with registration and authentification systems, example of blog site with posts and comments,
up vote and down vote system.


Features:
--------

- Bootstrap 3 with Jquery for frontend
- MySQL
- Flask-SQLAlchemy
- Google+ authentification with Oauth2
- Easy database migrations with Flask-Migrate
- Flask-WTForms for validation of form
- Unittest
- CSS and JS minification using webpack
- gunicorn and nginx as server

# Getting Started

Preparing Flask modules and Environment Variables
------------------------------------------------

For first clone this repository:

` git clone https://github.com/SandPipper/BasicFlaskApp `

And install pyvenv:

` sudo apt-get install pyvenv `

Create virtual environment for your project:

` pyvenv-3.5 name_of_your_environment `

Edit activate script in your virtual environment:

`nano name_of_your_environment/bin/activate `


Adding to the end of file your environment variables:

```
export DB_NAME='your_db_name'
export SECRET_KEY='your_secret_key'
export BLOG_ADMIN='your_mail_for_admin@gmail.com'
export MAIL_USERNAME='your_mail_for_admin@gmail.com'
export MAIL_PASSWORD='your_mail_for_admin_password'
export DB_USERNAME='your_mysql_user'
export DB_PASSWORD='your_mysql_password'
export DEV_DB_NAME='dev_blog_db'
export TEST_DB_NAME='test_blog_db'
export PROD_DB_NAME='prod_blog_db'
export FLASK_CONFIG='default'
export GOOGLE_CLIENT_ID='you_google_client_id'
export GOOGLE_CLIENT_SECRET='your_google_client_server'

```

Take your Google api credentails:

` https://console.developers.google.com/projectselector/apis/credentials/oauthclient `

Activate your virtual environment:

` source name_of_your_environment/bin/activate `

Install python packages from requirements:

` pip install -r requirements/dev.txt `



Install MySQL server and initialize data base
--------------------------------------------

Install MySQL server:

```
sudo apt-get update
sudo apt-get install mysql-server
```


Initialize data base and start migration script:

```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

To run it with gunicorn use `gunicorn --workers 3 --bind localhost manage:app --log-level debug`


Install and initialize nginx:
----------------------------

Install `sudo apt-get install nginx`


Configure it:

```
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-available/BasicFlaskApp
```


Put the next with edited by you path to root folder of project:

```
server {
    listen 80;
    server_name localhost;

    root /home/path/to/BasicFlaskApp;

    access_log /home/path/to/BasicFlaskApp/logs/nginx/access.log;
    error_log /home/path/to/BasicFlaskApp/logs/nginx/error.log;

    location / {
        proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        if (!-f $request_filename) {
            proxy_pass http://127.0.0.1:8000;
            break;
        }
    }

    location /static {
        alias /home/path/to/BasicFlaskApp/app/static/;
        autoindex on;
        add_header Cache-Control public;
    }

}
```


Save changes and create directory for logs:

` mkdir -p logs/nginx `


The lasts steps:

```
sudo ln -s /etc/nginx/sites-available/BasicFlaskApp /etc/nginx/sites-enabled/
sudo nginx -t
```

Now go to `localhost` and enjoy for this work application.

Unittests
---------
To run unittests execute next in root folder of app:

`python manage.py test`

A few word about webpack
------------------------

If you want change `.css` or `.js` files and rebundled it with webpack
install it `npm install webpack` and use ` webpack -p `

If you will have some problem with node.js ` sudo apt-get update && sudo apt-get install nodejs-legacy `
And don't forget install all dependences with ` npm i <package_name> `
