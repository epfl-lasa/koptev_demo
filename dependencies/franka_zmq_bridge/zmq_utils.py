import zmq
import time


def zmq_init_recv(socket):
    val = None
    while val is None:
        try:
            val = socket.recv_pyobj(flags=zmq.DONTWAIT)
            status = 1
        except:
            print("No input data! (yet) waiting...")
            time.sleep(0.1)
            pass
    return val


def zmq_try_recv(val, socket):
    status = 0
    try:
        val = socket.recv_pyobj(flags=zmq.DONTWAIT)
        status = 1
    except:
        pass
    return val, status


def zmq_try_recv_raw(val, socket):
    status = 0
    try:
        val = socket.recv(flags=zmq.DONTWAIT)
        status = 1
    except:
        pass
    return val, status


def init_subscriber(context, address, port):
    # socket to receive stuff
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.CONFLATE, 1)
    socket.connect("tcp://%s:%s" % (address, str(port)))
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    return socket


def init_subscriber_binding(context, address, port):
    # socket to receive stuff
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.CONFLATE, 1)
    socket.bind("tcp://%s:%s" % (address, str(port)))
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    return socket


def init_publisher(context, address, port):
    socket = context.socket(zmq.PUB)
    try:
        socket.bind("tcp://%s:%s" % (address, str(port)))  # Binding to all interfaces
        print(f"Publisher bound to tcp://0.0.0.0:{port}")
    except zmq.ZMQError as e:
        print(f"Failed to bind to address tcp://{address}:{port} - {e}")
    return socket
    
    #socket = context.socket(zmq.PUB)
    #socket.bind("tcp://%s:%s" % (address, str(port)))
    #return socket
