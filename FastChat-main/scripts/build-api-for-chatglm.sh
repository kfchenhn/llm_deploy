#!/bin/bash
# A rather convenient script for spinning up models behind screens


# Variables
PROJECT_DIR="$(pwd)"
CONDA_ENV_NAME="fastchat" #

# MODEL_PATH="/home/c205/workspace/models/Apollo-7B/" 
MODEL_PATH="/home/c205/workspace/models/THUDM/chatglm3-6b/" 
API_HOST="0.0.0.0"
API_PORT_NUMBER=8002


# init the screens
check_and_create_screen() {
    local SCREENNAME="$1"
    if screen -list | grep -q "$SCREENNAME"; then
        echo "Screen session '$SCREENNAME' exists. Doing nothing."
    else
        echo "Screen session '$SCREENNAME' not found. Creating..."
        screen -d -m -S "$SCREENNAME"
        echo "created!"
    fi
}

# convenience function for sending commands to named screens
send_cmd() {
    local SCREENNAME="$1"
    local CMD="$2"
    screen -DRRS $SCREENNAME -X stuff '$2 \r'
}

# hardcoded names, for baby api
SCREENNAMES=(
    "controller2"
    "api2"
    # Worker screens include the devices they are bound to, if 'd0' is only worker it has full GPU access
    "worker-d2"
  
)

for screen in "${SCREENNAMES[@]}"; do
    check_and_create_screen "$screen"
    sleep 0.1
    # also activate the conda compute environment for these
    screen -DRRS "$screen" -X stuff "^C^C"
    sleep 5
    screen -DRRS "$screen" -X stuff "conda deactivate \r"
    screen -DRRS "$screen" -X stuff "conda activate $CONDA_ENV_NAME \r"
    
done

# Send Commmands on a per Screen Basis
screen -DRRS controller2 -X stuff  "python3 -m fastchat.serve.controller --port 41001\r"

# screen -DRRS worker-d0 -X stuff  "CUDA_VISIBLE_DEVICES=0 python3 -m fastchat.serve.model_worker --model-path $MODEL_PATH  --conv-template one_shot --limit-worker-concurrency 1  \r"
screen -DRRS worker-d2 -X stuff  "CUDA_VISIBLE_DEVICES=2 python3 -m fastchat.serve.model_worker --model-path $MODEL_PATH --port 41002 --worker-address http://localhost:41002 --controller-address  http://localhost:41001 \r"

screen -DRRS api2 -X stuff  "python3 -m fastchat.serve.openai_api_server --host $API_HOST --port $API_PORT_NUMBER --controller-address  http://localhost:41001 \r"

# curl http://127.0.0.1:8000/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen-7B-QAnything","messages": [{"role": "user", "content": "Hello! What is your name?"}]}'