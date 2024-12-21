# chrono-shift

Daily scheduling and running of dynamic tasks not suitable for static cron configuration.
* NHL game starts by team
* Sunrise by location
* Sunset by location

### Deployment

#### Configure Server

Configuring for Ubuntu Server 24.04

* [Install docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) using apt, **not** snap 
* [Configure docker](https://docs.docker.com/engine/install/linux-postinstall/) to run as non-root user
* [Enable docker](https://docker-docs.uclv.cu/engine/install/linux-postinstall/#systemd) to run on start

#### Setup Heartbeat

* create `.env` file
* set `HEARTBEAT_ID=` according to heartbeat configuration at [betterstack](https://betterstack.com/)

#### Start Service

```bash
./start.sh
```

* Run service in detached mode
* Service will auto-restart due to `restart: always` in `docker-compose.yaml` when server reboots
