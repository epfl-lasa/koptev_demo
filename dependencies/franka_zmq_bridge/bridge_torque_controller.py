import numpy as np
import time
import zmq

import state_representation as sr
from controllers import create_joint_controller, CONTROLLER_TYPE
from network_interfaces.zmq import network

from zmq_utils import *

np.set_printoptions(precision=2, suppress=True)

# zmq parameters
state_address = "*:1701"
command_address = "*:1702"
context = zmq.Context(1)

subscriber = network.configure_subscriber(context, state_address, True)
publisher = network.configure_publisher(context, command_address, True)

command = network.CommandMessage()
command.control_type = [network.ControlType.EFFORT.value]

#mac_ip = "128.179.133.49"  # wifi
#mac_ip = "128.178.145.71"  # cable
# mac_ip = "128.178.145.38"
rtx_4090_ip = "128.178.145.74"
panda_pc = "128.178.145.78"
# zmq receive state from controller
socket_recieve_sim_state = init_subscriber(context, rtx_4090_ip, 1336)

# zmq send state to controller
# socket_send_robot_state = init_publisher(context, samurai_ip, 6969)
socket_send_robot_state = init_publisher(context, '0.0.0.0', 6969)


# Define controller and set gains
controller = create_joint_controller(CONTROLLER_TYPE.IMPEDANCE, 7)
# stiffness = sr.Parameter(
#     "stiffness", np.diag([80, 50, 50, 10, 8, 6, 1]), sr.ParameterType.MATRIX
# )
# damping = sr.Parameter(
#     "damping", np.diag([20, 10, 10, 5, 5, 5, 5]), sr.ParameterType.MATRIX
# )
stiffness = sr.Parameter(
    "stiffness",
    1.3 * np.diag([60.0, 60.0, 62.5, 50.0, 42.5, 20.0, 12.5]),
    sr.ParameterType.MATRIX,
)
damping = sr.Parameter(
    "damping",
    np.diag([25.0, 18.75, 22.5, 16.25, 12.5, 8.75, 5.0]),
    sr.ParameterType.MATRIX,
)

controller.set_parameter(stiffness)
controller.set_parameter(damping)
desired_jstate = sr.JointState("franka", 7)
current_jstate = sr.JointState("franka", 7)
# controller
q_desired = np.array([0.0, 0.0, 0.0, -2.0, 0.0, 1.68625, 0.85])
for i in range(1000):
    robot_state = network.receive_state(subscriber)
    if robot_state:
        q_desired = robot_state.joint_state.get_positions()
    time.sleep(0.002)
dq_desired = q_desired * 0

t0 = time.time()
max_torque = 5
last_command_time = t0
smoothing = 0.2
while True:
    robot_state = network.receive_state(subscriber)
    sim_state, sim_state_status = zmq_try_recv(None, socket_recieve_sim_state)
    # print(f"robot_state statsu {robot_state}")
    if sim_state_status:
        # print("Sim stuff!")
        # print(sim_state)
        q_desired = sim_state["q"].numpy()
        dq_desired = smoothing * dq_desired + (1 - smoothing) * sim_state["dq"].numpy()
        last_command_time = time.time()
    else:
        # dq_desired = 0.99 * dq_desired
        # print("No command from controller!")
        pass
    if time.time() - last_command_time > 1:  # 1 seconds
        dq_desired = dq_desired * 0.99
    if robot_state:
        # parse robot state
        q_current = robot_state.joint_state.get_positions()
        qdot_current = robot_state.joint_state.get_velocities()
        qddot_current = robot_state.joint_state.get_accelerations()
        # send robot state to controller
        socket_send_robot_state.send_pyobj(q_current)

        # feed into structure
        current_jstate.set_positions(q_current)
        current_jstate.set_velocities(qdot_current)
        current_jstate.set_accelerations(qddot_current)

        inertia = sr.Parameter(
            "inertia", robot_state.mass.get_value(), sr.ParameterType.MATRIX
        )
        controller.set_parameter(inertia)
        # print(
        #     f"Time since start: {(time.time() - t0):4.2f}\nJoint positions: {q_current}\nJoint velocities: {qdot_current}"
        # )
        # generate command
        desired_jstate.set_positions(q_desired)
        desired_jstate.set_velocities(dq_desired)
        desired_jstate.set_accelerations(0 * dq_desired)
        controller_compute = controller.compute_command(desired_jstate, current_jstate)
        torque_command = controller_compute.get_torques()
        torque_command = np.clip(torque_command, -max_torque, max_torque)
        command.joint_state = robot_state.joint_state

        # print(f"Torques command: {torque_command}\n")
        # print(f"Difference: {np.linalg.norm(q_current-q_desired)}\n")

        # if not sim_state_status:
        #     torque_command = torque_command * 0.0
        command.joint_state.set_torques(torque_command)
        network.send_command(command, publisher)
        time.sleep(0.001)
    else:
        print("no robot state!")
        pass
