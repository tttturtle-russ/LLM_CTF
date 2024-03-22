#!/bin/bash

# python main.py "./database/rev/rebug 2" "./prompts/prompts_open/rev/rebug2.txt"
# python main.py "./database/rev/whataxor" "./prompts/prompts_open/rev/whataxor.txt"

for chal in database/forensics/*; do
    base_chal=$(basename "$chal")
    touch "./logging/forensics/$base_chal".txt
    echo "Solving $base_chal, see in the log file"
#    python main.py --question="$chal" --model="$1" --prompt="./prompts/prompts_open/forensics/$base_chal".txt > "./logging/forensics/$base_chal".txt
    python main.py --question="$chal" --model="$1" > "./logging/forensics/$base_chal".txt
done