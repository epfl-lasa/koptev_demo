#!/bin/bash
IMAGE_NAME="koptev_demo"
IMAGE_TAG="latest"
CONTAINER_NAME="${IMAGE_NAME//[\/.]/-}"
USERNAME="developer"
MODE="interactive"
USE_NVIDIA_TOOLKIT=()

# Help
HELP_MESSAGE="Usage: ./start_dockers.sh [interactive | server | connect] [-i, --image] [-u, --user]
Build the '${IMAGE_NAME}' image.
Options:
  interactive            Spin the image in the console
  server                 Spin the image as an ssh server
  connect                Connects to an active container
  -i, --image            The name of the image to use to start the container
  -u, --user             Specify the name of the login user. (optional)
  -h, --help             Show this help message and the one from aica-docker
  Additional arguments are passed to the aica-docker command.
  "

# Argument parsing
RUN_FLAGS=()
FWS_FLAGS=()
SHOW_HELP=false

while [ "$#" -gt 0 ]; do
    case "$1" in
    -i | --image)
        IMAGE_NAME=$2
        shift 2
        ;;
    -u | --user)
        USERNAME=$2
        shift 2
        ;;
    -m | --mode)
        MODE=$2
        shift 2
        ;;
    -h | --help)
        SHOW_HELP=true
        shift 1
        ;;
    *)
        if [ -z "${MODE}" ]; then
            MODE=$1
        else
            FWD_ARGS+=("$1")
        fi
        shift 1
        ;;
    esac
done

# Help verbose
if $SHOW_HELP; then
    echo $HELP_MESSAGE
    aica-docker $MODE -h
    exit 1
fi

# Handle interactive/server specific arguments
if [ "${MODE}" != "connect" ]; then
    echo ${MODE}

    # Check if a conitainer with this name is already running
    if [ "$( docker container inspect -f '{{.State.Status}}' ${CONTAINER_NAME} 2>/dev/null)" == "running" ]; then
        echo "A container named ${CONTAINER_NAME} is already running. Stopping it."
        docker stop ${CONTAINER_NAME}
    fi

    # Check if a NVIDIA GPU is available
    if [[ $(sudo lshw -C display | grep vendor) =~ NVIDIA ]]; then
        USE_NVIDIA_TOOLKIT=true
        echo "Detected NVIDIA graphic card, giving access to the container."
    else
        USE_NVIDIA_TOOLKIT=false
    fi

    # network for ros
    FWD_ARGS+=(--net=host)
    FWD_ARGS+=(--no-hostname)
    #FWD_ARGS+=(--env ROS_HOSTNAME="$(hostname)")

    # Handle GPU usage
    if [ ${USE_NVIDIA_TOOLKIT} == true ]; then
    	#GPU_FLAG="--gpus all"
    	FWD_ARGS+=(--gpus="all")
    fi

    # Other
    FWD_ARGS+=("--privileged")

    # Add volumes for airhockey, toolkit, data, python and docker
    FWD_ARGS+=(--volume="${PWD}/dependencies/franka_zmq_bridge:/home/developer/franka_zmq_bridge:rw")
    FWD_ARGS+=(--volume="${PWD}/ds_mppi:/home/developer/ds_mppi:rw")

    echo "${FWD_ARGS[@]}"
fi

# Trick aica-docker into making a server on a host network container
if [ "${MODE}" == "server" ]; then
    FWD_ARGS+=("--detach")
    MODE=interactive
fi


# ${GPU_FLAG} \
# Start docker using aica
aica-docker \
    "${MODE}" \
    "${IMAGE_NAME}:${IMAGE_TAG}" \
    -u "${USERNAME}" \
    -n "${CONTAINER_NAME}" \
    "${FWD_ARGS[@]}" 
