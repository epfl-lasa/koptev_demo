include = -I./include
libpath = -L./lib
libs = -lNatNetLibShared -lzmq

all: OptiTrackZMQBridge

OptiTrackZMQBridge:
	g++ source/OptiTrackZMQBridge.cpp source/OptiTrackClient.cpp $(include) $(libpath) $(libs) -o run/OptiTrackZMQBridge

.PHONY: clean
clean:
	@rm -r ./run/*
