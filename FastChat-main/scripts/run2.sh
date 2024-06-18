#!/bin/bash
fuser -k -n tcp 20001
fuser -k -n tcp 20002
fuser -k -n tcp 8000
fuser -k -n tcp 8001

host=0.0.0.0
#model1
controller_port1=21001
worker_port1=31001
api_port1=8000
model_path1=/home/c205/workspace/models/Qwen-7B-QAnything
#model2
controller_port2=21002
worker_port2=31002
api_port2=8001
model_path2=/home/c205/workspace/models/Apollo-7B


##model1
# run_controller
python3 -m fastchat.serve.controller --host $host --port $controller_port1 > output1_1.log 2>&1 &
# run_worker
CUDA_VISIBLE_DEVICES=0,1 python3 -m  fastchat.serve.model_worker --host $host --controller-address http://$host:$controller_port1 --port $worker_port1 --model-path $model_path1 --max-gpu-memory 20GiB --num-gpus 2 > output1_2.log 2>&1 &
# run_api 
python3 -m fastchat.serve.openai_api_server --host $host --controller-address $host:$controller_port1 --port $api_port1 > output1_3.log 2>&1 &
##model2
python3 -m fastchat.serve.controller --host $host --port $controller_port2 > output2_1.log 2>&1 &
# run_worker
CUDA_VISIBLE_DEVICES=2,3 python3 -m  fastchat.serve.model_worker --host $host --controller-address http://$host:$controller_port2 --port $worker_port2 --model-path $model_path2 --max-gpu-memory 20GiB --num-gpus 2 > output2_2.log 2>&1 &
# run_api 
python3 -m fastchat.serve.openai_api_server --host $host --controller-address http://$host:$controller_port2 --port $api_port2 > output2_3.log 2>&1 &

