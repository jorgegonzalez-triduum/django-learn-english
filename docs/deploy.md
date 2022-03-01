Server: Ubuntu 18

Check python is installed

$python3

Or install with

sudo apt-get install python3

Install the following dependencies

sudo apt-get install software-properties-common
sudo apt-add-repository universe
sudo apt-get update
sudo apt-get install virtualenv
sudo apt-get install nginx
sudo apt-get install git

Creating deployers group

sudo addgroup deployers

Create app user
sudo useradd -M triduum_base
sudo usermod -L triduum_base
sudo usermod -s /bin/false  triduum_base
sudo usermod -a -G deployers triduum_base


Add current user to deployers
sudo usermod -a -G deployers ubuntu

Add nginx user to deployers group
sudo usermod -a -G deployers www-data


Creating directory structure
sudo mkdir -p /opt/deploy/{socks/triduum_base,envs,reps,tmp}
sudo mkdir -p /var/www/{static/triduum_base,media/triduum_base}

Modding
sudo chown root:deployers /opt/deploy /var/www/media /var/www/static -R
sudo chmod 770 /opt/deploy /var/www/media /var/www/static -R

Create apps sites available-enabled

sudo touch /etc/nginx/sites-available/triduum_base

Update the created file with this:

server{

      listen           8000;
      server_name      domain.triduum_base;

      location /static/ {
               autoindex off;
               alias /var/www/static/triduum_base/;
               expires 1h;
      }

      location /media/ {
               autoindex off;
               alias /var/www/media/triduum_base/;
      }

      location / {
             include proxy_params;
             proxy_pass http://unix:/opt/deploy/socks/triduum_base/triduum_base.sock;
      }

      error_page 500 502 503 504 /custom_50x.html;
      location = /custom_50x.html {
             root /usr/share/nginx/html;
             internal;
      }

}

Link the file to sites-enabled

sudo ln -s /etc/nginx/sites-available/triduum_base /etc/nginx/sites-enabled/

Disable the current default

sudo rm /etc/nginx/sites-enabled/default

Check nginx syntax is ok

sudo nginx -t

sudo service nginx restart


Create apps virtualenv

cd /opt/deploy/envs
virtualenv -p /usr/bin/python3 triduum_base

Activate virtualenv

source /opt/deploy/envs/triduum_base/bin/activate


Make sure your user has created a SSH key enrolled with the control version provider

Clone source code from control version

cd /opt/deploy/reps/
git clone https://bitbucket.org/triduum-inc/triduum-base.git --recursive
cd /opt/deploy/reps/triduum-base

Remember install first env_requirements.md after install pip requirements

Install pip requirements

pip install -r /opt/deploy/reps/triduum-base/requirements/base.txt

pip requirements to deploy

pip install gunicorn

Change secrets env

nano /opt/deploy/reps/triduum-base/triduum_base/config/secrets.json

Change EXEC_ENV value to the current deployment environment (DEV,TEST,PRODUCTION)

Test the runserver

cd /opt/deploy/reps/triduum-base/triduum_base/
python manage.py runserver 0:18000

Create app directories structure

Run gunicorn command

gunicorn --timeout 3600 --workers 3 --bind unix:/opt/deploy/socks/triduum_base/triduum_base.sock config.wsgi

Configure systemd service

sudo touch /etc/systemd/system/triduum_base.service

Update the created file with this:

[Unit]
Description=triduum_base daemon
After=network.target

[Service]
User=triduum_base
Group=deployers

WorkingDirectory=/opt/deploy/reps/triduum-base/triduum_base
ExecStart=/opt/deploy/envs/triduum_base/bin/gunicorn --timeout 3600 --workers 20 --bind unix:/opt/deploy/socks/triduum_base/triduum_base.sock config.wsgi

[Install]
WantedBy=multi-user.target



Now, execute:

set os on-restart enabled service

sudo systemctl enable triduum_base
sudo service triduum_base restart
sudo service triduum_base status


Manage.py operations:

Migrate app
cd /opt/deploy/reps/triduum-base/triduum_base/
python manage.py migrate
python manage.py collectstatic

Check config/settings/env:
Constants MEDIA_ROOT AND STATIC_ROOT corresponds to the created dirs on /var/www/

Restart app and nginx again

sudo service triduum_base restart
sudo service nginx restart

check from external IP:PORT the access to the app

Note:

- Remember add external access on the cloud provider firewalls
- Always execute, in each action, modding commands to ensure the correct permissions to all deployment files (Including statics and medias)


