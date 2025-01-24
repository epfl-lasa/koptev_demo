import numpy as np
import time
import zmq


from network_interfaces.zmq import network

np.set_printoptions(precision=2, suppress=True)
state_address = "*:1701"
command_address = "*:1702"
context = zmq.Context(1)

subscriber = network.configure_subscriber(context, state_address, True)
publisher = network.configure_publisher(context, command_address, True)

command = network.CommandMessage()
command.control_type = [network.ControlType.EFFORT.value]

target_position = np.array([0.0, 0.0, 0.0, -2.0, 0.0, 1.68625, 0.855323])
t0 = time.time()
ctr = 0
max_torque = 1
gain = 10
damping = 3
while True:
    state = network.receive_state(subscriber)
    if state:
        # print(state)
        q_current = state.joint_state.get_positions()
        qdot_current = state.joint_state.get_velocities()
        print(
            f"Time since start: {time.time() - t0}\nJoint positions: {q_current}\n Joint velocities: {qdot_current}\n"
        )
        delta = target_position - q_current

        print(f"Delta: {delta}")

        command.joint_state = state.joint_state

        desired_torques = gain * delta - damping * qdot_current
        print(f"Torques command: {desired_torques}\n")

        command.joint_state.set_torques(desired_torques)
        network.send_command(command, publisher)
        time.sleep(0.001)
