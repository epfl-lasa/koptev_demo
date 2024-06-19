# Optitrack

This directory contains an Optitrack client that streams the Optitrack data over *NatNet* and publishes the data to a
ZMQ socket.

## Usage

Given that you have a gcc/g++ compiler installed on the computer, run

```bash
make all
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PWD/lib
```

This will build the executables and put them into the `run` folder. Then,

```bash
cd run
./OptiTrackZMQBridge
```

You should see the markers and rigid bodies that are currently activated in Motive. In another terminal, check that the
bridge is working:

```bash
./SampleClient
```

then press 1. You should now see the data that is received from Motive and published to ZMQ.

### Docker
There is a simple docker wrapper to directly startup the optitrack.  
For this use in this directory:
Build docker:
``` bash
bash docker-build.sh
```
Run docker:
``` bash
bash docker-run.sh
```

# NatNet SDK 3.1 and SampleClient

The headers and shared library for the NatNet SDK as well as the SampleClient.cpp source file were created by
NaturalPoint and were retrieved from this archive:
https://s3.amazonaws.com/naturalpoint/software/NatNetSDKLinux/ubuntu/NatNet_SDK_3.1_ubuntu.tar

The files have been copied into this directory for convenience.

Running the SampleClient on Linux
========================================

This Readme file contains first time instructions for building and running the NatNetSDK for Linux.

Note:

* The NatNetSDK for Linux will only work on 64 bit operating systems.
* For up-to-date information, visit:
  http://wiki.optitrack.com/index.php?title=NatNet:_Sample_Projects

<!-- TODO: add ZMQ dependency once the CMake project is complete -->

1.[Linux] Install necessary programs and libraries. In order to build and run the SampleClient application on Linux,
there are two essential requirements. The gcc/g++ compiler must be installed on the machine.

- Ubuntu Terminal Instructions

  `sudo apt-get install build-essential`

- Fedora Terminal Instructions

  `sudo dnf install gcc-c++`

<!-- TODO: fix the following build steps once the CMake project is complete -->

2.[Linux] Navigate to the NatNetSDK directory. Open a shell prompt and set the directory to the samples/SampleClient
folder in the uncompressed NatNet SDK directory.

3.[Linux] Build the sample. While in the SampleClient directory, enter make clean all and compile the sample.

4.[Linux] Once the sample is built, navigate to the build output folder.

5.[Linux] Set an environment variable for the library path. In order to run compiled NatNetSDK samples, the directory of
the NatNet library
(libNatNetLibShared.so)    must be specified. To do this, set up an environment variable for defining the path to the
library file directory:

- export LD_LIBRARY_PATH=$LD_LIBRARY_PATH: {lib folder directory}

6.[Motive] Start an Optitrack server (Motive). Motive needs to run on a Windows machine and the data needs to be
streamed through the connected network using the Data Streaming pane. Take a note of the server IP address from the Data
Streaming pane in Motive. Make sure to stream onto a network that the Linux machine is connected to; not local loopback
nor the camera network.

8.[Linux] Start SampleClient.exe. Now, Start the client application from shell. Once the application starts, it will
search the networks and list out available tracking servers. From the list, select the Optitrack server from the above
step to start receiving tracking data.

- ./SampleClient.exe

## Authors / Maintainers

For any questions or further explanations, please contact the authors.

- Enrico Eberhard ([enrico.eberhard@epfl.ch](mailto:enrico.eberhard@epfl.ch))
