#pragma once

#include <cstdint>

namespace optitrack::proto {

struct RigidBody {
  int32_t id;
  float meanError;

  float x;
  float y;
  float z;

  float qw;
  float qx;
  float qy;
  float qz;
};

}