import numpy as np
import time
import zmq

import state_representation as sr
from controllers import create_joint_controller, CONTROLLER_TYPE
from network_interfaces.zmq import network

np.set_printoptions(precision=2, suppress=True)

# zmq parameters
state_address = "*:1601"
command_address = "*:1602"
context = zmq.Context(1)

subscriber = network.configure_subscriber(context, state_address, True)
publisher = network.configure_publisher(context, command_address, True)

command = network.CommandMessage()
command.control_type = [network.ControlType.EFFORT.value]

# Define controller and set gains
controller = create_joint_controller(CONTROLLER_TYPE.IMPEDANCE, 7)
stiffness = sr.Parameter(
    "stiffness", np.diag([5, 10, 5, 8, 8, 6, 3]), sr.ParameterType.MATRIX
)
damping = sr.Parameter(
    "damping", np.diag([10, 5, 5, 4, 4, 4, 1]), sr.ParameterType.MATRIX
)
controller.set_parameter(stiffness)
controller.set_parameter(damping)
desired_jstate = sr.JointState("franka", 7)
current_jstate = sr.JointState("franka", 7)
# controller
q_desired = np.array([0.0, 0.0, 0.0, -2.0, 0.0, 1.68625, 0.855323])

t0 = time.time()
ctr = 0
gain = 10
damping = 3
while True:
    robot_state = network.receive_state(subscriber)
    if robot_state:
        # parse robot state
        q_current = robot_state.joint_state.get_positions()
        qdot_current = robot_state.joint_state.get_velocities()
        current_jstate.set_positions(q_current)
        current_jstate.set_velocities(qdot_current)

        inertia = sr.Parameter(
            "inertia", robot_state.mass.get_value(), sr.ParameterType.MATRIX
        )
        controller.set_parameter(inertia)
        print(
            f"Time since start: {time.time() - t0}\nJoint positions: {q_current}\n Joint velocities: {qdot_current}\n"
        )
        # generate command
        desired_jstate.set_positions(q_desired)
        desired_jstate.set_velocities(q_desired * 0)

        delta = q_desired - q_current

        print(f"Delta: {delta}")
        controller_compute = controller.compute_command(desired_jstate, current_jstate)
        torque_command = controller_compute.get_torques()

        desired_state = robot_state

        command.joint_state = robot_state.joint_state

        print(f"Torques command: {torque_command}\n")

        command.joint_state.set_torques(torque_command)
        network.send_command(command, publisher)
        time.sleep(0.001)
