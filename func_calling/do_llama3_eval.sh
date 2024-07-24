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
    for year in 2015 2016; do
        for chal in chals/CTF/CSAW-CTF-${year}-Quals/"${category}"/*/challenge.json; do
            chalname=$(basename "$(dirname "$chal")")
            for i in {1..10}; do
                log="logs/${category}/${chalname}/conversation.llama3.${i}.json"
                analysis="analysis/${category}/${chalname}/analysis.llama3.${i}.json"
                if [ -f "${log}" ]; then
                    printf '[%02d/10] skipping %s attempting %s/%s; log exists\n' $i llama3 "${category}" "${chalname}"
                    continue
                fi
                cleanup_container
                printf '[%02d/10] %s attempting %s/%s\n' $i llama3 "${category}" "${chalname}"
                python llm_ctf_solve.py -d -M llama3 -m 30 -L "${log}" -A "${analysis}" "${chal}"
            done
        done
    done
done