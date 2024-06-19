import numpy as np
import time
import zmq
from zmq_utils import *


context = zmq.Context(1)

# zmq receive state from controller
socket = init_subscriber(context, "128.178.145.79", 5511)
while True:
    data, success = zmq_try_recv_raw(None, socket)
    print(success, data)
    time.sleep(0.01)
