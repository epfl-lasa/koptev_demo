#pragma once

#include <zmq.hpp>

#include "OptiTrackClient.h"
#include "optitrack_zmq_proto.h"

namespace optitrack {

class OptiTrackZMQBridge {
public:
  OptiTrackZMQBridge();
  ~OptiTrackZMQBridge();

  bool connect(const std::string& serverIP, const std::string& uri);
  void checkOptiTrackConnection();
  void publishCallback(sFrameOfMocapData* data);

  bool connected = false;

private:
  bool configureZMQ(const std::string& uri);
  void publish(const proto::RigidBody& rb);

  std::unique_ptr<OptiTrackClient> client_ = nullptr;
  std::unique_ptr<zmq::context_t> zmqContext_ = nullptr;
  std::unique_ptr<zmq::socket_t> zmqPublisher_ = nullptr;
};

}

