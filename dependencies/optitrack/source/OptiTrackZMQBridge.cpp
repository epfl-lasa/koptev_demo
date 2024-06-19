#include "optitrack/OptiTrackZMQBridge.h"
#include <iostream>
#include <chrono>

#include <cstdio>

#include "optitrack/optitrack_zmq_proto.h"

namespace optitrack
{
  OptiTrackZMQBridge::OptiTrackZMQBridge()
  {
    client_ = std::make_unique<OptiTrackClient>();
    zmqContext_ = std::make_unique<zmq::context_t>(1);
    // std::string hostname{"127.0.0.1"};
    // uint16_t port = 5511;
    // sock = ::socket(AF_INET, SOCK_DGRAM, 0);  // destination.sin_family = AF_INET;
    // destination.sin_port = htons(port);  // destination.sin_addr.s_addr = inet_addr(hostname.c_str());
  }
  OptiTrackZMQBridge::~OptiTrackZMQBridge()
  {
    if (zmqPublisher_ != nullptr)
    {
      zmqPublisher_->close();
    }
    zmqContext_.reset();
    zmqPublisher_.reset();
    client_.reset(); // ::close(sock);
  }
  bool OptiTrackZMQBridge::connect(const std::string &serverIP,
                                   const std::string &publishURI)
  {
    if (client_->connect(serverIP) != ErrorCode::ErrorCode_OK)
    {
      printf("[connect] Could not connect to OptiTrack server!\n");
      return false;
    }
    if (!configureZMQ(publishURI))
    {
      printf("[connect] Could not configure ZMQ publisher!\n");
      return false;
    }
    client_->setCallback([this](auto data)
                         { publishCallback(data); });
    connected = true;
    return true;
  }
  void OptiTrackZMQBridge::checkOptiTrackConnection()
  {
    client_->testConnection();
    client_->requestDataDescription();
  }
  bool OptiTrackZMQBridge::configureZMQ(const std::string &uri)
  {
    if (zmqPublisher_ != nullptr && zmqPublisher_->connected())
    {
      printf("[configureZMQ] Publisher already connected!\n");
      return true;
    }
    if (zmqContext_->handle() != nullptr)
    {
      zmqPublisher_ = std::make_unique<zmq::socket_t>(*zmqContext_, ZMQ_PUB);
      zmqPublisher_->bind("tcp://" + uri);
      zmqPublisher_->setsockopt(ZMQ_SNDHWM, 1);
      zmqPublisher_->setsockopt(ZMQ_CONFLATE, 1);
      printf("[configureZMQ] Publisher connected.\n");
      return true;
    }
    return false;
  }
  void OptiTrackZMQBridge::publishCallback(sFrameOfMocapData *data)
  {
    int nbodies = 0;
    std::vector<optitrack::proto::RigidBody> bodyArray;
    for (int32_t body = 0; body < data->nRigidBodies; ++body)
    {
      // 0x01 : bool, rigid body was successfully tracked in this frame
      bool trackingValid = data->RigidBodies[body].params & 0x01;
      if (trackingValid)
      {
        optitrack::proto::RigidBody rb{
            .id = data->RigidBodies[body].ID,
            .meanError = data->RigidBodies[body].MeanError,
            .x = data->RigidBodies[body].x,
            .y = data->RigidBodies[body].y,
            .z = data->RigidBodies[body].z,
            .qw = data->RigidBodies[body].qw,
            .qx = data->RigidBodies[body].qx,
            .qy = data->RigidBodies[body].qy,
            .qz = data->RigidBodies[body].qz};
        nbodies += 1;
        bodyArray.push_back(rb);
        // publish(rb);    // std::string msg = "Jane Doe";
        // char * msg = (char*)&rb;    // int n_bytes = ::sendto(sock, msg, sizeof(proto::RigidBody), 0, reinterpret_cast<sockaddr*>(&destination), sizeof(destination));
        // std::cout << n_bytes << " bytes sent" << std::endl;
      }
    }
    if (zmqPublisher_ == nullptr || !zmqPublisher_->connected())
      return;
    zmq::message_t message(nbodies * sizeof(proto::RigidBody));
    memcpy(message.data(), bodyArray.data(), nbodies * sizeof(proto::RigidBody));
    zmqPublisher_->send(message, zmq::send_flags::none);
    const auto tnow = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    // std::cout << nbodies * sizeof(proto::RigidBody) << " Bytes sent!" << tnow << std::endl;
  }
  void OptiTrackZMQBridge::publish(const proto::RigidBody &rb)
  {
    if (zmqPublisher_ == nullptr || !zmqPublisher_->connected())
    {
      return;
    }
    zmq::message_t message(sizeof(proto::RigidBody));
    memcpy(message.data(), &rb, sizeof(proto::RigidBody));
    zmqPublisher_->send(message, zmq::send_flags::none);
  }
}
int main(int, char **)
{
  optitrack::OptiTrackZMQBridge bridge;
  // if (!bridge.connect("128.178.145.104", "0.0.0.0:5511"))
  if (!bridge.connect("128.178.145.172", "0.0.0.0:5511"))
  {
    return -1;
  }
  bridge.checkOptiTrackConnection();
  while (bridge.connected)
  {
    // let the callback stream any received optitrack data over ZMQ
  }
  return 0;
}
