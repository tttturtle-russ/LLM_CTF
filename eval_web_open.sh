#!/bin/bash

for chal in database/web/*; do
    base_chal=$(basename "$chal")
    touch "./logging/web/$base_chal".txt
    echo "Solving $base_chal, see in the log file"
    python main.py --question="$chal" --model="$1" > "./logging/web/$base_chal".txt
done

# touch "./logging/circles.txt"
# echo "Solving circles, see in the log file"
# python main.py ./database/crypto/circles > ./logging/circles.txt