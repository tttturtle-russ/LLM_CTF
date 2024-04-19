python -u -m vllm.entrypoints.openai.api_server \
    --model /home/haoyang/Mistral-7B-Instruct-v0.2 \
    --host 0.0.0.0 \
    --max-model-len 29000

#python3 -m fastchat.serve.controller --host 127.0.0.1 &
#
#python3 -m fastchat.serve.vllm_worker --host 127.0.0.1 \
#    --controller-address http://127.0.0.1:21001 \
#    --model mistralai/Mistral-7B-Instruct-v0.2 &
#
#python3 -m fastchat.serve.openai_api_server --host 127.0.0.1 \
#    --controller-address http://127.0.0.1:21001 \
#    --port 8000 &