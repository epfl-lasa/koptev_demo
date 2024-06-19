import numpy as np
import time
import zmq


from network_interfaces.zmq import network


state_address = "*:1601"
command_address = "*:1602"
context = zmq.Context(1)

subscriber = network.configure_subscriber(context, state_address, True)
publisher = network.configure_publisher(context, command_address, True)

command = network.CommandMessage()
command.control_type = [network.ControlType.VELOCITY.value]

target_position = np.array([0.0, 0.0, 0.0, -2.0, 0.0, 1.68625, 0.855323])
t0 = time.time()
ctr = 0

while True:
    state = network.receive_state(subscriber)
    if state:
        # print(state)
        q_current = state.joint_state.get_positions()
        qdot_current = state.joint_state.get_velocities()
        print(
            f"Time since start: {time.time() - t0}\n Joint positions: {q_current}\n Joint velocities: {qdot_current}\n\n"
        )
        desired_velocity = (target_position - q_current) * 0.1
        print(f"Desired velocity: {desired_velocity}")
        print(type(desired_velocity))

        command.joint_state = state.joint_state
        command.joint_state.set_velocities(desired_velocity)
        network.send_command(command, publisher)
        time.sleep(0.001)
