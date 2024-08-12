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
    categories="pwn web crypto rev forensics misc"
else
    categories="$@"
fi

for category in $categories; do
    for chal in ./chals/"${category}"/*/challenge.json; do
        chalname=$(basename "$(dirname "$chal")")
        for i in {1..10}; do
            log="logs/${category}/${chalname}/conversation.Mistral-7B-Instruct-v0.2.${i}.json"
            analysis="analysis/${category}/${chalname}/analysis.Mistral-7B-Instruct-v0.2.${i}.json"
            if [ -f "${log}" ]; then
                printf '[%02d/10] skipping %s attempting %s/%s; log exists\n' $i /home/haoyang/Mistral-7B-Instruct-v0.2 "${category}" "${chalname}"
                continue
            fi
            cleanup_container
            printf '[%02d/10] %s attempting %s/%s\n' $i /home/haoyang/Mistral-7B-Instruct-v0.2 "${category}" "${chalname}"
            python llm_ctf_solve.py -d -M mistralai/Mistral-7B-Instruct-v0.2 -m 30 -L "${log}" -A "${analysis}" "${chal}"
        done
    done
done
