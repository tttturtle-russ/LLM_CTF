import llm_ctf.local_mixtral_task as local_mixtral
import llm_ctf.mixtral_task as mixtral
import llm_ctf.deepseek_task as deepseek
import sys
import os
import json
import argparse
from pathlib import Path


EXPERIMENT_REPEAT = 10
DEFAULT_PATH = Path(__file__).parent.resolve()

parser = argparse.ArgumentParser(description="use command line args to choose model and challenge type", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--model', '-m', help="specify model to use", required=True)
parser.add_argument("--question", '-q', help="specify question relavent path", required=True)
parser.add_argument("--prompt", '-p', help="sepcify prompt relavent path")
args = parser.parse_args()
def main(question_path, prompt_path, chal_config):
    
    os.chdir(DEFAULT_PATH)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    task = None
    try:
        if args.model == "Mixtral":
            task = mixtral.MixtralTask(
                question_path=question_path,
                task_config=chal_config,
                url_path=os.path.abspath("./keys/mixtral_api.txt")
            )
        elif args.model == "LocalMixtral":
            task = local_mixtral.LocalMixtralTask(
                question_path=question_path,
                task_config=chal_config,
            )
        elif args.model == "DeepSeek":
            task = deepseek.DeepSeekTask(
                question_path=question_path,
                task_config=chal_config,
            )
        else:
            raise RuntimeError("Unknown model name")
    except Exception as e:
        print(f"\033[91mRuntimeError: {e}")
        exit(1)
    resp = task.task_prompt(prompt=prompt_path, use_file=False, append_msg="", template_prompt=True)
    # print("============================== RESPONSE FROM MODEL ==============================")
    # print(resp)
    task.save_code(resp)
    solved = task.validate_sol(resp)
    return solved
    
if __name__ == "__main__":
    # p = subprocess.run("sudo docker run --rm -it -v $PWD:/opt/exp ctfenv /bin/bash -c \'cd /opt/exp/solutions/rev/\"Rebug 1\"&&python sol.py\'", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5, shell=True)

    # print(str('\n' + p.stdout.decode("utf-8")))
    # if len(sys.argv) != 3:
    #     print("Usage: python script.py <question_path> <prompt_path>")
    #     sys.exit(1)
        
    question_path = args.question
    prompt_path = args.prompt
    try:
        with open(os.path.join(question_path, "challenge.json"), 'r') as f:
            chal_json = json.load(f)
    except FileNotFoundError as e:
        print(f"\033[91m{e}\nPlease specify right question path")
        exit(1)

    success = 0
    chal_name = chal_json["name"]
    for i in range(EXPERIMENT_REPEAT):
        try:
            if main(question_path, prompt_path, chal_json):
                success += 1
        except Exception as e:
            print(e)
    
    with open("results.txt", "a+") as f: 
        res = f"Challenge: {chal_name}, Success: {success}/{EXPERIMENT_REPEAT}\n"
        f.write(res)
        print(res)