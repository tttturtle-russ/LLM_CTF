#!/bin/bash

for chal in database/pwn/*; do
    base_chal=$(basename "$chal")
    touch "./logging/pwn/$base_chal".txt
    echo "Solving $base_chal, see in the log file"
#    python main.py --question="$chal" --model="$1" --prompt="./prompts/prompts_open/pwn/$base_chal".txt > "./logging/pwn/$base_chal".txt
    python main.py --question="$chal" --model="$1" > "./logging/pwn/$base_chal".txt
done