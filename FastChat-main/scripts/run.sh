fuser -k -n tcp 20001
fuser -k -n tcp 20002
fuser -k -n tcp 8000
fuser -k -n tcp 8001
# CUDA_VISIBLE_DEVICES=0,1 python scripts/build-api.py --model_name llm-for-rag-7b --model_path /home/c205/workspace/models/Qwen-7B-QAnything --worker_port 21001 --api_port 8000 --num_gpus 2  > output1.log 2>&1 &
CUDA_VISIBLE_DEVICES=2,3 python scripts/build-api.py --model_name whucs-med-7b --model_path /home/c205/workspace/models/Apollo-7B --args.controller_port_port 21002 --api_port 8001  --num_gpus 2 > output2.log 2>&1 &