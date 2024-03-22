#!/bin/bash

for chal in database/crypto/*; do
    base_chal=$(basename "$chal")
    touch "./logging/crypto/$base_chal".txt
    echo "Solving $base_chal, see in the log file"
#    python main.py --question="$chal" --model="$1" --prompt="./prompts/prompts_open/crypto/$base_chal".txt > "./logging/crypto/$base_chal".txt
    python main.py --question="$chal" --model="$1" > "./logging/crypto/$base_chal".txt
done

# touch "./logging/circles.txt"
# echo "Solving circles, see in the log file"
# python main.py ./database/crypto/circles > ./logging/circles.txt