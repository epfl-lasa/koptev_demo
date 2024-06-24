FROM ghcr.io/epfl-lasa/control-libraries/development-dependencies:20.04 as source-dependencies

RUN apt-get update && apt-get install -y \
  featherpad \
  libzmq3-dev \
  libsodium-dev \
  nano \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN wget https://github.com/zeromq/cppzmq/archive/v4.7.1.tar.gz -O cppzmq-4.7.1.tar.gz && tar -xzf cppzmq-4.7.1.tar.gz
RUN cd cppzmq-4.7.1 && mkdir build && cd build && cmake .. -DCPPZMQ_BUILD_TESTS=OFF && sudo make install
RUN rm -rf cppzmq*

WORKDIR /tmp
ARG CONTROL_LIBRARIES_BRANCH=v6.3.1
RUN git clone -b ${CONTROL_LIBRARIES_BRANCH} --depth 1 https://github.com/epfl-lasa/control-libraries.git
RUN cd control-libraries/source && ./install.sh --auto --no-dynamical-systems
RUN cd control-libraries/protocol && ./install.sh --auto
RUN pip3 install control-libraries/python

RUN git clone -b v1.1.0 --depth 1 https://github.com/aica-technology/network-interfaces
RUN cd network-interfaces && sudo bash install.sh --auto --no-cpp

RUN rm -rf /tmp/*

# install pyzmq
RUN pip3 install pyzmq

# Install ds_mppi with PyEnv
WORKDIR ${HOME}
COPY --chown=${USER} ./ds_mppi ./ds_mppi
COPY --chown=${USER} ./dependencies/franka_zmq_bridge ./franka_zmq_bridge

RUN sudo pip install torch==1.13.1 scipy pybullet pillow matplotlib

ENTRYPOINT /bin/bash
