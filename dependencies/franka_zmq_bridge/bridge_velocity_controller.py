import numpy as np
import time
import zmq

import state_representation as sr
from controllers import create_joint_controller, CONTROLLER_TYPE
from network_interfaces.zmq import network

from zmq_utils import *

np.set_printoptions(precision=2, suppress=True)

# zmq parameters
state_address = "*:1601"
command_address = "*:1602"
context = zmq.Context(1)

subscriber = network.configure_subscriber(context, state_address, True)
publisher = network.configure_publisher(context, command_address, True)

command = network.CommandMessage()
command.control_type = [network.ControlType.VELOCITY.value]

mac_ip = "128.179.133.49"  # wifi
mac_ip = "128.178.145.71"  # cable
# zmq receive state from controller
socket_recieve_sim_state = init_subscriber(context, mac_ip, 1336)

# zmq send state to controller
socket_send_robot_state = init_publisher(context, "*", 6969)

# Define controller and set gains

for i in range(1000):
    robot_state = network.receive_state(subscriber)
    if robot_state:
        q_desired = robot_state.joint_state.get_positions()
    time.sleep(0.001)
dq_desired = q_desired * 0

t0 = time.time()
last_command_time = t0
smoothing = 0.95
while True:
    robot_state = network.receive_state(subscriber)
    sim_state, sim_state_status = zmq_try_recv(None, socket_recieve_sim_state)
    if sim_state_status:
        print("Sim stuff!")
        # print(sim_state.numpy())
        q_desired = sim_state["q"].numpy()
        dq_desired = smoothing * dq_desired + (1 - smoothing) * sim_state["dq"].numpy()
        last_command_time = time.time()
    else:
        # dq_desired = 0.99 * dq_desired
        print("No command from controller!")
    if time.time() - last_command_time > 1:  # 1 seconds
        dq_desired = dq_desired * 0.95
    if robot_state:
        # parse robot state
        q_current = robot_state.joint_state.get_positions()
        qdot_current = robot_state.joint_state.get_velocities()
        qddot_current = robot_state.joint_state.get_accelerations()
        # send robot state to controller
        socket_send_robot_state.send_pyobj(q_current)

        print(
            f"Time since start: {(time.time() - t0):4.2f}\nJoint positions: {q_current}\nJoint velocities: {qdot_current}"
        )

        desired_velocity = q_desired + dq_desired * 1 - q_current

        command.joint_state = robot_state.joint_state
        command.joint_state.set_velocities(desired_velocity)

        network.send_command(command, publisher)
        time.sleep(0.001)
    else:
        print("no robot state!")
