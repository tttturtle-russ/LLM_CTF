#!/usr/bin/env bash

# Build main docker image
docker build -t ctfenv .

# Build docker image for each challenge
for d in database/{pwn,crypto}/*; do
    if [ -d "$d" ]; then
        echo "Building $d"
        image_name=$(jq -r .container_image < "$d"/challenge.json)
        docker build -t "$image_name" "$d"
    fi
done


# Create network
docker network create ctfnet

# Download and unpack Ghidra
if [ ! -d ghidra_11.0_PUBLIC ]; then
    wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0_build/ghidra_11.0_PUBLIC_20231222.zip
    unzip ghidra_11.0_PUBLIC_20231222.zip
    rm ghidra_11.0_PUBLIC_20231222.zip
fi

for d in database/*; do
    if [ -d "$d" ]; then
        mkdir -p "./logging/${d#database/}"
    fi
done

mkdir -p keys
touch keys/mixtral_api.txt
echo "If you want to use Mixtral API, fill your mixtral_api in keys/mixtral_api.txt"