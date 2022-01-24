# OEE Monitoring Webapp

This project was made to monitor OEE for machines

This constitutes the central server, which can receive live OEE data from client and is accessed through a flask webapp.

The app is accompanied by an Android app, which connects to the server and takes manual input to set the state of its assigned machine.


## Setup
(Tested on Ubuntu 20.04)

Run `npm install` in the `/app/static` directory.

Rename `config.py.example` to `config.py` and edit config options.

Run `pip install -r requirements.txt` in a virtual environment if necessary.

Change start.sh to be executable `chmod 755 start.sh` and run it.
(This requires gunicorn to be installed)

The software ideally uses nginx as a reverse proxy. This can be install with `sudo apt install nginx`. An example config is included in this repo. In order for the android app to work correctly, the proxy server must pass on the IP address of the android client. 

The app uses redis as a Celery broker, which is needed for periodic tasks. Redis can be installed with `sudo apt install redis` and modifying the address in `config.py` if necessary


## Documentation



## Demo mode

When run with `DEMO_MODE=True` in the `config.py` file, the app will fake inputs. On startup it will backfill missed data. The celery worker will fake inputs as long as the app is running.

