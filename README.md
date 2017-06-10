# aslo-v3
Upcoming Software center for SugarLabs (ASLO V3)


## Setup Instructions

### Install virtualenv

`pip install virtualenv`

### Create a vritualenv
`virtualenv ~/envs/flask-dev`

### Activate virtualenv
`source ~/envs/flask-dev/bin/activate`

### Install Dependencies
`pip install -r requirements.txt`

### Install Redis

``` bash

cd /tmp
wget http://download.redis.io/releases/redis-stable.tar.gz
tar xzf redis-stable.tar.gz
make
make test
sudo make install
```
 For a more comprehensive guide follow this [Tutorial from DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04)

Make sure redis is running by logging in `redis-cli`

### Install MongoDB
Make sure MongoDB is running by typing `mongo`

### Install Docker
Make sure docker is installed and running

##### Build the docker image

```bash 
cd build-bot
docker build . -t build-bot
```
### Run Celery Workers

`celery worker -A app.celery --loglevel=info` this will start celery workers
### Run the Flask Server

`python app.py` will start Flask server listening on all interfaces `0.0.0.0` and port `5000`

## Building
Temporarily all apps are cloned to a folder named repos.
So create a folder named `repos`.

 `mkdir repos`.

#### Installing Build Dependencies

Install `sugar-toolkit`

Clone
```bash
git clone --depth=1 https://github.com/sugarlabs/sugar-toolkit-gtk3

```

Install it at appropriate location

``` bash
mv sugar-toolkit-gtk3/src/sugar3 ~/envs/flask-dev/lib/python2.7/site-packages/sugar3;
```

Create soft link for old Gtk 2 apps

```bash
ln -s  ~/envs/flask-dev/lib/python2.7/site-packages/sugar3  ~/envs/flask-dev/lib/python2.7/site-packages/sugar
```
