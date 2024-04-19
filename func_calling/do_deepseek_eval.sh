#!/usr/bin/env bash

function cleanup_container {
    docker stop ctfenv &> /dev/null
    docker wait ctfenv &> /dev/null
    docker rm ctfenv &> /dev/null
    while docker container inspect ctfenv &> /dev/null ; do
        echo "Waiting for ctfenv to be removed..."
        sleep 1
    done
}

if [ $# -eq 0 ]; then
    categories="rev pwn web crypto forensics misc"
else
    categories="$@"
fi

for category in $categories; do
    for model in /home/haoyang/deepseek-coder-6.7b-base; do
        for chal in chals/"${category}"/*/challenge.json; do
            chalname=$(basename "$(dirname "$chal")")
            model_name=$(basename "${model}")
            for i in {1..10}; do
                log="logs/${category}/${chalname}/conversation.${model_name}.${i}.json"
                if [ -f "${log}" ]; then
                    printf '[%02d/10] skipping %s attempting %s/%s; log exists\n' $i "${model}" "${category}" "${chalname}"
                    continue
                fi
                cleanup_container
                printf '[%02d/10] %s attempting %s/%s\n' $i "${model}" "${category}" "${chalname}"
                python llm_ctf_solve.py -d -M ${model} -m 30 -L "${log}" "${chal}"
            done
        done
    done
done