#!/bin/bash
docker run \
	   -it \
	   -e DISPLAY=$DISPLAY \
	   -h $HOSTNAME \
	   -u root \
	   --net host \
	   optitrack_zmq
