# Mikhail Koptev's Obstacle Avoidance Demo README

This code comes from several repositories and has been re-structured to be used easily to start Mikhail KOPTEV's Obstacle Avoidance demo at LASA.

## Structure 
This demo uses 3 dockers :
- franka-lightweight-interface: to be run on the computer connected to the panda, used to communicate with the robot
- optitrack : used to publish optitrack info using zmq, should be run on SAMURAI
- koptev-demo : used to run all python code from Mikhail, should be run on SAMURAI (except franka_zmq_bridge which MAY need to be run on computer connected to panda)

Note : docker commands rely on [aica-docker scripts](https://github.com/aica-technology/docker-images) which should be installed on compputers sued for the demo.

## TODO 
- document which adresses need changing (add to config.yaml : zmq: IP: o SAMURAI, panda_PC, link them in ds_mppi scripts )
- load config.yaml in bridge_torque_controller.py (or modif code directly)
- check if possible to run bridge_torque_controller on samurai and communicate with fwli 
- remove config_real if not relevant
- make docker compose ?


## RUN DEMO

Open the 3 docker containers :
- fwli on computer connected to panda
- optitrack and koptev-demo on SAMURAI

Make sure the IP adresses are correct and communication runs smoothly. These can be checked in the ds_mppi/config.yaml file 

Then run the following commands.

### Terminal 1 - Connect to the robot
On Panda_PC
```console
cd ~/Workspace/koptev_demo/dependencies/franka-lightweight-interface
bash run-rt.sh
franka_lightweight_interface 17 panda_ --sensitivity low --joint-damping off
```

### Terminal 2 - Optitrack bridge
On SAMURAI
```console
cd ~/Workspace/koptev_demo/dependencies/optitrack
bash docker-build.sh (IF never build before)
bash docker-run.sh
```

### Build and start docker commands
All the next commands must be run from inside the koptev-demo container, which can be build and start with these commands :
```console
cd ~/Workspace/koptev_demo
bash docker/build-image.sh
bash docker/start-docker.sh
```

### Terminal 3 - Torque control bridge for robot
On SAMURAI
```console
cd ~/Workspace/koptev_demo
bash docker/start-docker.sh -m connect
cd franka_zmq_bridge/
python3 bridge_torque_controller.py
```

### Terminal 4 - Tracking obstacles with optitrack
On SAMURAI
```console
cd ~/Workspace/koptev_demo
bash docker/start-docker.sh -m connect
cd ds_mppi/
python3 obstacleStreamerOptitrack.py
```
### Terminal 5 - Pybullet Simulation
On Panda_PC (if doesn't slow things down)
```console
cd ~/Workspace/koptev_demo
bash docker/start-docker.sh -m connect
cd ds_mppi/
python3 pbSim.py
```

### Terminal 6 - Integrator Feedback
On SAMURAI
```console
cd ~/Workspace/koptev_demo
bash docker/start-docker.sh -m connect
cd ds_mppi/
python3 frankaIntegratorFeedback.py
```

### Terminal 7 - Optimization for concave obstacles 
On SAMURAI
Planner (optim thingy) for concave obstacles -> do not launch unless you have good computer
```console
cd ~/Workspace/koptev_demo
bash docker/start-docker.sh -m connect
cd ds_mppi/
python3 frankaPlanner.py
```

## Sources 
Code originally comes from these repos and has been restructured to be easily used : 

https://github.com/epfl-lasa/OptimalModulationDS

https://github.com/m-koptev/franka_zmq_bridge

https://github.com/m-koptev/optitrack_lasa


## Authors/Maintainers

Mikhail KOPTEV (mikhail.koptev@epfl.ch)
Maxime GAUTIER (maxime.gautier@epfl.ch)
