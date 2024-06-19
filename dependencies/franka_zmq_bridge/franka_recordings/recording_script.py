import numpy as np
import time
import zmq
from pynput import keyboard
from network_interfaces.zmq import network
import os

np.set_printoptions(precision=4, suppress=True)
state_address = "*:1601"
command_address = "*:1602"
context = zmq.Context(1)

subscriber = network.configure_subscriber(context, state_address, True)
publisher = network.configure_publisher(context, command_address, True)

command = network.CommandMessage()
command.control_type = [network.ControlType.EFFORT.value]

target_position = np.array([0.0, 0.0, 0.0, -2.0, 0.0, 1.68625, 0.855323])
t0 = time.time()
ctr = 0
max_torque = 5
gain = 10
damping = 3
rec_flag = False

#########################
#### LOGGING SETUP ######
#########################
folder_name = time.strftime("%Y-%m-%d_%H-%M-%S")
# create folder
os.makedirs("recordings_data/" + folder_name)

#########################
#### KEYBOARD CONTROL ###
#########################
# "a" - reset attractor to current position
# "space" - start recording
# "enter" - stop recording


def on_press_fcn(key):
    # im very sad to use global variables here, but alternative is to wrap events into lambda functions
    global target_position, rec_flag, t_rec, filename, rec_data
    try:
        key = key.char  # single-char keys
    except:
        key = key.name  # other keys
    if key == "a":
        target_position = q_current
        print(
            time.time(),
            "Resetting target position to current position: ",
            target_position,
        )
    if key == "space":
        print(time.time(), "Starting recording!")
        rec_flag = True
        t_rec = time.time()
        filename = (
            "recordings_data/"
            + folder_name
            + "/rec_"
            + time.strftime("%H-%M-%S")
            + ".txt"
        )
        rec_data = np.empty((0, 15), dtype=np.float64)
    if key == "enter":
        print(time.time(), "Saving the trajectory...")
        rec_flag = False
        with open(filename, "w") as f:
            np.savetxt(f, rec_data, delimiter=",")


listener = keyboard.Listener(on_press=on_press_fcn)
listener.start()


#########################
##### MAIN LOOP #########
#########################

while True:
    state = network.receive_state(subscriber)
    if state:
        # parse robot state
        q_current = state.joint_state.get_positions()
        qdot_current = state.joint_state.get_velocities()
        # write to data array
        if rec_flag:
            print(time.time() - t_rec)
            print(q_current)
            print(qdot_current)
            data_arr = np.concatenate(
                [np.array([time.time() - t_rec]), q_current, qdot_current]
            )
            new_line = np.expand_dims(data_arr, axis=0)
            rec_data = np.append(rec_data, new_line, axis=0)

        desired_torques = gain * (target_position - q_current) - damping * qdot_current
        torques_norm = np.linalg.norm(desired_torques)
        if torques_norm > max_torque:
            desired_torques = desired_torques / torques_norm * max_torque

        command.joint_state = state.joint_state  # copy current state
        command.joint_state.set_torques(desired_torques)  # inject desired torques
        network.send_command(command, publisher)
        time.sleep(0.01)
