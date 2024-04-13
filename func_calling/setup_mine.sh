#!/usr/bin/env bash

for d in chals/CSAW-CTF-2023-Finals/{pwn,crypto,web,misc}/*; do
    if [ -d "$d" ]; then
        echo "Building $d"
        image_name=$(jq -r .container_image < "$d"/challenge.json)
        is_compose=$(jq -r .compose < "$d"/challenge.json)
        if [ "$is_compose" = "true" ]; then
            docker compose -f "$d"/docker-compose.yml build
        elif [ "$image_name" = "null" ]; then
            continue
        else
            docker build -t "$image_name" "$d"
        fi
    fi
done