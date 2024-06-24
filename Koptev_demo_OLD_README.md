# Mikhail Koptev's Obstacle Avoidance Demo README

## Docker commands

See koptev_docker/README.md for detailed instructions. 
Open a termnial window and split in 3.

### Terminal 1
```console
cd ~/Workspace/franka-lightweight-interface
bash run-rt.sh
franka_lightweight_interface 17 panda_ --sensitivity low --joint-damping off
```

 DO NOT USE DOCKER FOR THESE -> does not work 

### Terminal 2
```console
cd ~/Workspace/Mikhail_DEMO/koptev_docker/source/franka_zmq_bridge
python3 bridge_torque_controller.py
```

### Terminal 3
```console
cd ~/Workspace/Mikhail_DEMO/koptev_docker/source/optitrack
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PWD/lib
run/OptiTrackZMQBridge 
```
 
### Terminal 2 - DOCKER
```console
cd /home/lasa/Workspace/Mikhail_DEMO/koptev_docker
aica-docker connect koptev-demo-container
cd franka_zmq_bridge/
python3 bridge_torque_controller.py
```

### Terminal 3 - DOCKER
```console
cd /home/lasa/Workspace/Mikhail_DEMO/koptev_docker
aica-docker connect koptev-demo-container
cd optitrack/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PWD/lib
run/OptiTrackZMQBridge 
```

## Local commands

Make sure the PyEnv is activated :

- add this line to ~/.bashrc : alias source_dsmod="source /home/lasa/Workspace/Mikhail_DEMO/pyEnv/dsmod/bin/activate"

Open another terminal window, cd to correct folder and split in 4 

Need to install pytorch==1.13.1 and scipy, pybullet
Change ip adress to local one (search 128.178.145. and modify relevant places)

### Terminal 4
Mikahail's package
Obstacle tracking
```console
cd /home/lasa/Workspace/Mikhail_DEMO/ds_mppi
source_dsmod
python3 obstacleStreamerOptitrack.py
```
### Terminal 5
Pybullet simulation -> not needed, only for display
```console
cd /home/lasa/Workspace/Mikhail_DEMO/ds_mppi
source_dsmod
python3 pbSim.py
```

### Terminal 6
Integrator feedback
```console
cd /home/lasa/Workspace/Mikhail_DEMO/ds_mppi
source_dsmod
python3 frankaIntegratorFeedback.py
```
### Terminal 7
Planner (optim thingy) for concave obstacles -> do not launch unless you have good computer
```console
cd /home/lasa/Workspace/Mikhail_DEMO/ds_mppi
source_dsmod
python3 frankaPlanner.py
```

## Sources 
Code originally comes from these repos and has been restructured to be easily used : 

https://github.com/epfl-lasa/OptimalModulationDS
https://github.com/m-koptev/franka_zmq_bridge
https://github.com/m-koptev/optitrack_lasa

### Old instructions 

These are viable for panda_pc or any computer with all requirements installed : aica's control libraries 6.3.1, network interfaces v1.1, both with python bindings, franka-lightweight-interface, and PyEnv 

maybe some other stuff like pyzmq? See import errors


Standard communication tools:
terminal 1:
cd Workspace/franka_lightweight_interface
git checkout main #(OPTIONAL - make sure you are on correct branch)
bash run-rt.sh
franka_lightweight_interface 17 panda_ --sensitivity low --joint-damping off

terminal 2:
cd ~/Workspace/Mikhail_DEMO/koptev/franka_zmq_bridge
python3 bridge_torque_controller.py


terminal 3: 
cd ~/Workspace/Mikhail_DEMO/koptev/optitrack
run/OptiTrackZMQBridge 



Mikahail's package
Obstacle tracking
cd /home/alberic/Documents/LASA/OptimalModulationDS/python_scripts/ds_mppi
source_dsmod
python3 obstaclesStreamerOptitrack.py


Pybullet simulation
cd /home/alberic/Documents/LASA/OptimalModulationDS/python_scripts/ds_mppi
source_dsmod
python3 pbSim.py

Integrator feedback
cd /home/alberic/Documents/LASA/OptimalModulationDS/python_scripts/ds_mppi
source_dsmod
python3 frankaIntegratorFeedback.py

Planner (optim thingy)
cd /home/alberic/Documents/LASA/OptimalModulationDS/python_scripts/ds_mppi
source_dsmod
python3 frankaPlanner.py

