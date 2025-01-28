import yaml, sys
import torch
import numpy as np
sys.path.append('functions/')
from zmq_utils import *
from optitrack_utils import *
from copy import deepcopy
from scipy.spatial.transform import Rotation as R
import numpy as np

def read_yaml(fname):
    with open(fname) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config

# define tensor parameters (cpu or cuda:0 or mps)
params = {'device': 'cpu', 'dtype': torch.float32}
# NEEDED TO USE GPU -> create all tensors on GPU 
# torch.set_default_tensor_type('torch.cuda.FloatTensor')

def get_robot_pos(bodies):
    for body in bodies:
    #     print(f"optitrack ID {body['id']}")
    #     print(f"optitrack is ID 1096 {body['id'] == 1096}")
        if body['id'] == 1096: # or 1:
            # print(f"optitrack ROBOT {body['pos']}")
            return body['pos']
    return torch.tensor([5.5629, -0.1130,  0.4499])

def get_ball_pos(bodies, radius, robot_pos):
    for body in bodies:
        # print(f"optitrack ID {body['id']}")
        # print(f"optitrack is ID 1001 {body['id'] == 1001}")
        if body['id'] == 1001: # or 1:
            # print(f"optitrack BALL {body['pos']}")
            # print(f"optitrack BALL - robot {body['pos'] - robot_pos}")
            ball_frame_corrected = body['pos'] - robot_pos
            ball_frame_corrected_final = torch.tensor([-ball_frame_corrected[0],
                                                       ball_frame_corrected[2],
                                                       ball_frame_corrected[1]])
            # print(f"optitrack  ball_frame_corrected {ball_frame_corrected_final}")
            return torch.hstack([ball_frame_corrected_final, torch.tensor(radius)])
    return torch.tensor([10, 10, 10, torch.tensor(radius)])

def transform_pos_to_robot_frame(bodies, robot_pos):
    id_list= [1001, 1002, 1003, 1004, 1005, 1006, 1007]
    for body in bodies:
        if body['id'] in id_list:
            pos_corrected = body['pos'] - robot_pos
            pos_corrected_final = torch.tensor([-pos_corrected[0],
                                                pos_corrected[2],
                                                pos_corrected[1]])
            body['pos'] = pos_corrected_final
    return bodies


def get_human_pos(bodies, markers = None):
    ls = lambda n: torch.linspace(0, 1, n).unsqueeze(-1)
    body_obs = torch.empty((0,4))
    back = torch.tensor([])

    shoulder_width = 0.4
    pelvis_width = 0.2
    back_width_n = 7
    back_height_n = 6
    back_radius = 0.07
    arm_n = 5
    arm_radius = 0.05
    shoulder_line = []
    if markers is None:
        markers = dict()
    for body in bodies:
        if body['id'] == 1002:
            markers['neck'] = body
        if body['id'] == 1003:
            markers['pelvis'] = body
        if body['id'] == 1004:
            markers['right_elbow'] = body
            markers['right_elbow']['pos'] = markers['right_elbow']['pos'] + \
                                            markers['right_elbow']['rot']@torch.tensor([0, 0, -0.03])
        if body['id'] == 1005:
            markers['right_wrist'] = body
            markers['right_wrist']['pos'] = markers['right_wrist']['pos'] + \
                                            markers['right_wrist']['rot']@torch.tensor([-0.03, 0, -0.03])
        if body['id'] == 1006:
            markers['left_elbow'] = body
            markers['left_elbow']['pos'] = markers['left_elbow']['pos'] + \
                                           markers['left_elbow']['rot']@torch.tensor([0, 0, -0.03])
        if body['id'] == 1007:
            markers['left_wrist'] = body
            markers['left_wrist']['pos'] = markers['left_wrist']['pos'] + \
                                           markers['left_wrist']['rot']@torch.tensor([-0.03, 0, -0.03])
    ## create shoulder line from neck marker
    if 'neck' in markers.keys():
        l_shoulder_pos = markers['neck']['pos'] + markers['neck']['rot']@torch.tensor([0.1, -0.5*shoulder_width,0.1])
        r_shoulder_pos = markers['neck']['pos'] + markers['neck']['rot']@torch.tensor([0.1, 0.5*shoulder_width,0.1])
        shoulder_line = l_shoulder_pos + ls(back_width_n) * (r_shoulder_pos - l_shoulder_pos)
        head_sph = markers['neck']['pos'] + markers['neck']['rot']@torch.tensor([0.1, 0, 0.3])
        head = torch.hstack([head_sph, torch.tensor(0.15)])

    if 'pelvis' in markers.keys():
        l_hip_pos = markers['pelvis']['pos'] + markers['pelvis']['rot']@torch.tensor([0.1, -0.5*pelvis_width,0])
        r_hip_pos = markers['pelvis']['pos'] + markers['pelvis']['rot']@torch.tensor([0.1, 0.5*pelvis_width,0])
        hip_line = l_hip_pos + ls(back_width_n) * (r_hip_pos - l_hip_pos)

    if 'neck' in markers.keys() and 'pelvis' in markers.keys():
        back_linspaced = hip_line + ls(back_height_n).unsqueeze(1) * (shoulder_line - hip_line)
        back_pos = back_linspaced.view(-1, 3)
        back = torch.hstack([back_pos, torch.zeros(len(back_pos), 1) + back_radius])
        body_obs = torch.vstack([body_obs, back, head])

    if len(shoulder_line) > 0 and 'right_elbow' in markers.keys() and 'right_wrist' in markers.keys():
        r_arm_1 = shoulder_line[-1] + ls(arm_n) * (markers['right_elbow']['pos'] - shoulder_line[-1])
        r_arm_2 = markers['right_elbow']['pos'] + ls(arm_n) * (markers['right_wrist']['pos'] - markers['right_elbow']['pos'])
        r_arm = torch.vstack([r_arm_1, r_arm_2])
        r_arm = torch.hstack([r_arm, torch.zeros(len(r_arm), 1) + arm_radius])
        body_obs = torch.vstack([body_obs, r_arm])

    if len(shoulder_line) > 0 and 'left_elbow' in markers.keys() and 'left_wrist' in markers.keys():
        l_arm_1 = shoulder_line[0] + ls(arm_n) * (markers['left_elbow']['pos'] - shoulder_line[0])
        l_arm_2 = markers['left_elbow']['pos'] + ls(arm_n) * (markers['left_wrist']['pos'] - markers['left_elbow']['pos'])
        l_arm = torch.vstack([l_arm_1, l_arm_2])
        l_arm = torch.hstack([l_arm, torch.zeros(len(l_arm), 1) + arm_radius])
        body_obs = torch.vstack([body_obs, l_arm])

    return markers, body_obs
def main_loop():

    config = read_yaml('config.yaml')

    ########################################
    ###            ZMQ SETUP             ###
    ########################################
    context = zmq.Context()
    # socket to publish obstacles
    socket_send_obs = init_publisher(context, 'localhost' , config["zmq"]["obstacle_port"])

    # socket to receive data from optitrack (pc1)
    # socket_receive_optitrack = init_subscriber(context, '128.178.145.38', 5511)
    socket_receive_optitrack = init_subscriber(context, '0.0.0.0', 5511) 


    # socket to receive data from optitrack (pc2)
    # socket_receive_optitrack = init_subscriber(context, '128.178.145.5', 5511)

    freq = config["obstacle_streamer"]["frequency"]
    t_0 = time.time()
    N_ITER = 0
    state = None
    # create square pointcloud at table base
    human_dict = None
    n_dummy = 100
    obs = torch.hstack((torch.zeros(n_dummy, 3) + 10, torch.zeros(n_dummy, 1) + 0.05)).to(**params)

    pos0 = torch.tensor([0.7, -0.5, 0.0])
    rot0 = torch.tensor(R.from_euler('xyz', [0, 0, 90], degrees=True).as_matrix()).to(**params)
    body_arr = [dict() for i in range(6)]
    body_arr[0]['pos'] = torch.zeros(3) + pos0 + torch.tensor([0, 0, 0.4])
    body_arr[0]['rot'] = rot0
    body_arr[0]['id'] = 1002 # neck
    body_arr[1]['pos'] = torch.zeros(3) + pos0
    body_arr[1]['rot'] = rot0
    body_arr[1]['id'] = 1003 # pelvis
    body_arr[2]['pos'] = torch.zeros(3) + pos0 + torch.tensor([-0.4, -0.1, 0.5])
    body_arr[2]['rot'] = rot0
    body_arr[2]['id'] = 1004 # right elbow
    body_arr[3]['pos'] = torch.zeros(3) + pos0 + torch.tensor([-0.4, -0.2, 0.75])
    body_arr[3]['rot'] = rot0
    body_arr[3]['id'] = 1005 # right wrist
    body_arr[4]['pos'] = torch.zeros(3) + pos0 + torch.tensor([0.4, -0.1, 0.5])
    body_arr[4]['rot'] = rot0
    body_arr[4]['id'] = 1006 # left elbow
    body_arr[5]['pos'] = torch.zeros(3) + pos0 + torch.tensor([0.4, -0.2, 0.75])
    body_arr[5]['rot'] = rot0
    body_arr[5]['id'] = 1007 # left wrist

    use_single_obstacle = True

    while True:
        moved = False
        t_run = time.time() - t_0

        # get robot state
        optitrack_data, optitrack_recv_status = zmq_try_recv_raw(None, socket_receive_optitrack)

        # print(f"optitrack status {optitrack_recv_status}")
        # print(f"optitrack optitrack_data {optitrack_data}")

        if optitrack_recv_status:
            bodies = process_raw_message(optitrack_data, params)
            # print(bodies)
            # if len(bodies) > 0:
            if len(bodies) > 0:
                if use_single_obstacle:
                    robot_pos = get_robot_pos(bodies)
                    obs[0] = get_ball_pos(bodies, 0.2, robot_pos)
                else:
                    robot_pos = get_robot_pos(bodies)
                    bodies_transformed = transform_pos_to_robot_frame(bodies, robot_pos)
                    human_dict, human_spheres = get_human_pos(bodies_transformed, human_dict)
                    n_sph = len(human_spheres)
                    if n_sph > 0:
                        obs = human_spheres
                        moved = True

                # print(f"obs: {obs}")
                # print("BALL : ", bodies)
        socket_send_obs.send_pyobj(obs)
        time.sleep(1/freq)
        N_ITER += 1
        if N_ITER % freq == 0:
            print(f"Streaming at {freq} Hz for {int(t_run):d} seconds.")

if __name__ == '__main__':
    main_loop()
