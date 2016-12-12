# Bird or Squirrel

The smart bird feeder that tweets pictures of anything inside. This app uses a Raspberry Pi, camera, and motion sensor. See the howchoo guide for an overview.

## Installation

Clone the repository.

Install the required Python packages.

`sudo pip install -r requirements.txt`

Install supervisor.

`sudo apt-get install supervisor`

Copy the supervisor configuration file.

`cp birdorsquirrel-supervisor.conf /etc/supervisor/conf.d/`

Update and start supervisor.

```
sudo service supervisor restart
sudo supervisorctl update
sudo supervisorctl restart birdorsquirrel
```
