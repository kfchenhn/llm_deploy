import subprocess
import threading
import os
from argparse import ArgumentParser


# os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"
# Using 127.0.0.1 because localhost does not work properly in Colab

def run_controller(controller_port):
    subprocess.run(["python3", "-m", "fastchat.serve.controller", "--host", "127.0.0.1", "--port", controller_port])

def run_model_worker(controller_port, worker_port, model_path, num_gpus):
    subprocess.run(["python3", "-m", "fastchat.serve.model_worker", "--host", "127.0.0.1", "--controller-address", "http://127.0.0.1:"+controller_port, "--port", worker_port, "--model-path", model_path, "--max-gpu-memory", "20GiB","--num-gpus", num_gpus])

def run_api_server(controller_port,api_port):
    subprocess.run(["python3", "-m", "fastchat.serve.openai_api_server", "--host", "127.0.0.1", "--controller-address", "http://127.0.0.1:"+controller_port, "--port", api_port])


if __name__ == "__main__":
    #CUDA_VISIBLE_DEVICES=0,1 python scripts/build-api.py --model_name llm-for-rag-7b --model_path /home/c205/workspace/models/Qwen-7B-QAnything --controller_port 21001 --worker_port 31001 --api_port 8000 --num_gpus 2  > output1.log 2>&1 &
    parser = ArgumentParser()
    parser.add_argument('--model_name',type=str, default='llm-for-rag-7b')
    parser.add_argument('--model_path',type=str, default='/home/c205/workspace/models/Qwen-7B-QAnything')
    parser.add_argument('--controller_port',type=str, default='21001')
    parser.add_argument('--worker_port',type=str, default='31001')
    parser.add_argument('--api_port',type=str, default='8000')
    parser.add_argument('--num_gpus',type=str, default='1')
    args = parser.parse_args()

    # run_controller(args.controller_port)
    # run_model_worker(args.controller_port, args.worker_port, args.model_path, args.num_gpus)
    # run_api_server(args.controller_port,args.api_port)


    controller_thread = threading.Thread(target=run_controller(args.controller_port))
    controller_thread.start()

    # Start model worker thread

    # see `controller.log` on the local storage provided by Colab
    # important to wait until the checkpoint shards are fully downloaded
    model_worker_thread = threading.Thread(target=run_model_worker(args.controller_port, args.worker_port, args.model_path, args.num_gpus))
    model_worker_thread.start()
    # Start API server thread
    api_server_thread = threading.Thread(target=run_api_server(args.controller_port,args.api_port))
    api_server_thread.start()

