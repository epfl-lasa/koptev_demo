import numpy as np
import time
import zmq


from network_interfaces.zmq import network


state_address = "*:1601"
command_address = "*:1602"
context = zmq.Context(1)

subscriber = network.configure_subscriber(context, state_address, True)
publisher = network.configure_publisher(context, command_address, True)
t0 = time.time()
ctr = 0
while True:
    state = network.receive_state(subscriber)
    if state:
        print(state)
    print()
    time.sleep(0.1)
