#!/bin/bash

for chal in database/misc/*; do
    base_chal=$(basename "$chal")
    touch "./logging/misc/$base_chal".txt
    echo "Solving $base_chal, see in the log file"
#    python main.py --question="$chal" --model="$1" --prompt="./prompts/prompts_open/misc/$base_chal".txt > "./logging/misc/$base_chal".txt
    python main.py --question="$chal" --model="$1" > "./logging/misc/$base_chal".txt
done
