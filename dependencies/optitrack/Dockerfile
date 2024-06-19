FROM ubuntu:22.04

# INSTALL NECESSARY PACKAGES
USER root
RUN apt update
RUN apt install -y build-essential wget
RUN echo "deb http://download.opensuse.org/repositories/network:/messaging:/zeromq:/release-stable/Debian_9.0/ ./" >> /etc/apt/sources.list
RUN wget https://download.opensuse.org/repositories/network:/messaging:/zeromq:/release-stable/Debian_9.0/Release.key -O- | apt-key add
RUN apt-get install -y libzmq3-dev
RUN apt clean

RUN mkdir /optitrack
WORKDIR /optitrack
COPY --chown=${USER} lib lib
COPY --chown=${USER} source source
COPY --chown=${USER} include include
COPY --chown=${USER} makefile makefile

RUN mkdir run
RUN make all

WORKDIR /optitrack
ENTRYPOINT export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PWD/lib && run/OptiTrackZMQBridge


