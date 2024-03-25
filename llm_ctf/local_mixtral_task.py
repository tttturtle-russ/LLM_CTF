import re
import os
import shutil
from .utils.ctflogging import Status
from .utils.ghidra_call import Ghidra_Call
from .utils.dockertool import DockerHelper
from .models.local_mixtral import LocalMixtral
from .prompt import *
import logging


class LocalMixtralTask:

    def __init__(self, question_path: str, task_config: dict):
        self.log = Status()
        self.config = task_config
        self.chal_name = self.config["name"]
        self.chal_path = os.path.abspath(question_path)
        self.model = self.mixtral_init()
        self.valid = False
        self.real_flag = self.config["flag"] \
            if isinstance(self.config["flag"], str) \
            else self.config["flag"]["content"]
        self.challenge_container = self.config.get("container_image", None)
        self.decomp_file = self.config.get("decomp_file", None)
        self.chal_category = self.config.get("category", "tmp")
        self.sol_path = os.path.join("./solutions", self.chal_category, self.chal_name)
        self.files = self.config["files"]
        self.proto = self.config.get("proto", None)
        self.port = self.config.get("internal_port", None)
        self.description = self.config.get("description", "No description provided by this challenge.")
        if not os.path.exists(self.sol_path):
            os.makedirs(self.sol_path)
        self.init_task()
        if self.decomp_file:
            self.ghidra = Ghidra_Call(self.sol_path, self.decomp_file)
            self.decomp()
        self.extra_info = []
        self.read_dir()
        self.docker_container = self.config.get("container_image", None)
        self.player_docker = "ctfenv"
        self.docker_tool = DockerHelper(self.player_docker)
        print("test: finish init")

    def read_dir(self):
        for i in self.files:
            with open(os.path.join(self.sol_path, i), "r") as f:
                try:
                    self.extra_info.append(i + ":\n" + f.read())
                except Exception as e:
                    continue
        if self.decomp_file:
            self.extra_info.append(self.ghidra._read_dump()["decomp"])

    def _clean_sol(self):
        if os.path.exists(self.sol_path):
            shutil.rmtree(self.sol_path)

    def decomp(self):
        print(self.log.assistant_message(f"Binary file {self.decomp_file} found, do reverse engineering..."))
        self.ghidra.run_ghidra()

    def init_task(self):
        print(self.log.assistant_message("Init solution folder..."))
        self._clean_sol()
        # shutil.copytree(self.chal_path, self.sol_path)
        shutil.copytree(self.chal_path, self.sol_path, copy_function=shutil.copy2)

    def mixtral_init(self):
        model = LocalMixtral(
            # "mistralai/Mixtral-8x7B-Instruct-v0.1"
            "mistralai/Mistral-7B-Instruct-v0.2"
        )

        return model

    def _extract_code(self, text):
        print(self.log.assistant_message("Format solver"))
        python_pattern = r'```python\n(.*?)```'
        matches = re.findall(python_pattern, text, re.DOTALL)
        if matches:
            print("Python solver found:")
            print(matches[0].strip())
            return matches[0].strip(), "Python"

        bash_pattern = r'```bash\n(.*?)```'
        matches = re.findall(bash_pattern, text, re.DOTALL)
        if matches:
            print("Bash solver found:")
            print(matches[0].strip())
            return matches[0].strip(), "Bash"

        print("No bash solver or python solver found in response")
        return None, None


    def extract_python_code(self, text):
        print(self.log.assistant_message("Format solver"))
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            print("Solver found:")
            print(matches[0].strip())
            return matches[0].strip()
        else:
            return None

    def extract_bash_code(self, text):
        print(self.log.assistant_message("Format solver"))
        pattern = r'```bash\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            print("Solver found:")
            print(matches[0].strip())
            return matches[0].strip()
        else:
            return None

    def task_prompt(self, prompt, use_file=False, append_msg="", template_prompt=True):
        if use_file:
            with open(prompt, 'r') as f:
                prompt = f.read()

        if template_prompt:
            prompt = PROMPT_INIT.format(category=self.chal_category,
                                        category_description=category_friendly[self.chal_category],
                                        name=self.chal_name, files=",".join(self.files), description=self.description)
            if self.port:
                if self.proto == "nc":
                    prompt += PROMPT_NC_INFO.format(container_image=self.docker_container, challenge_port=self.port)
                else:
                    prompt += PROMPT_PORT_INFO.format(container_image=self.docker_container, challenge_port=self.port)
        print(self.log.user_message(prompt + '\n' + "\n".join(self.extra_info) + append_msg))
        resp = self.model.generate(prompt + "\n".join(self.extra_info), append_msg=append_msg)
        print(self.log.assistant_message(resp))
        return resp

    def forward(self, resp_text):
        resp = ""
        code, _type = self._extract_code(resp_text)
        while _type is None and code is None:
            print(self.log.user_message("No Bash or Python code was found. Regenerating response now"))
            resp = self.model.generate("", retry=True)
            print(self.log.assistant_message(resp_text))
            code, _type = self._extract_code(resp_text)
        if _type == "Bash":
            return resp, code
        elif _type == "Python":
            self.save_code(code)
            return resp, code
        return None, None


    def save_code(self, code: str, file_name="sol.py"):
        print(self.log.assistant_message(f"Saving python code to {file_name}..."))
        with open(os.path.join(self.sol_path, file_name), 'w') as f:
            f.write(code)

    def validate_sol(self, resp: str, cmd: str):

        print(self.log.assistant_message(f"Checking solution..."))
        # print("============================== CHECKING SOLUTION ==============================")
        if self.real_flag in resp:
            print(f"Validation succeeded with returned flag {self.real_flag} in answer")
            self.valid = True
            return self.valid
        # print("============================== CHECKING FLAG IN SOLVER.PY ==============================")
        # os.chdir(self.sol_path)
        # subprocess.run(['chmod', "777", self.sol_path + "/*"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5)
        try:
            p = self.docker_tool.docker_exec(cmd,
                                             f"/opt/exp/solutions/{self.chal_category}/\"{self.chal_name}\"")
            # p = subprocess.run(['python', "sol.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5)
            res: str = str('\n' + p.stdout.decode("utf-8"))
        except Exception as e:
            print(f"Validation failed, solver cannot be executed or solver execution error, message shown below:")
            print(e)
            return self.valid

        if self.real_flag in res:
            print(f"Validation succeeded with returned flag {self.real_flag} by solver")
            self.valid = True
            return self.valid
        print(f"Validation failed, the result of code execution returned is: \n {res}")
        return self.valid
