"""
logger.py is used to record the logs of the assistant and user messages.
And record the logs of the tools used and code generated by the assistant.
"""
import json
import logging
import os.path
from pathlib import Path
from typing import Union, List, Dict
import re
import difflib

from util import CodeParser, SimilarityCalculator


class Logger:
    def __init__(self, log_file, logger, gold_file):
        self.log_file = Path(log_file)
        self.logdir = self.log_file.parent
        self.logdir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
        self.json = {}
        self.content = []
        self.finish_reason = "unknown"
        with open(gold_file, "r") as f:
            self.gold = json.load(f)
        self.len = len(self.gold)
        self.gold_path = None
        self.score = 0.0


    def log(self, message: str):
        if self.logger:
            self.logger.log(level=logging.DEBUG, msg=message)

    def compare_step(self, step, gold_step):
        """
        compare_step compares response of agent and gold
        :param step: response that agent generated
        :param gold_step: the exactly correct step
        :return: None
        """
        _type = gold_step["type"]
        if "thought" == _type:
            return
        else:
            if "code" in step:
                self.score += self._compare_ast(step["code"], gold_step["content"])
            if "tools" in step:
                self.score += self._compare_command(step["tools"]["arguments"]["command"], gold_step["content"])

    def compare_path(self, path):
        """
        compare_path compares a series of responses and the gold path
        :param path:
        :return:
        """
        for step, gold_step in zip(path, self.gold_path):
            self.compare_step(step, gold_step)

    def write_to_file(self):
        obj = {"results": self.content, "finish_reason": self.finish_reason, "score": self.score}
        with open(self.log_file, "w") as f:
            json.dump(obj, f, indent=4)

    @staticmethod
    def _compare_thought(thought, gold_thought):
        return difflib.SequenceMatcher(None, thought, gold_thought).quick_ratio()

    @staticmethod
    def _compare_ast(code, gold_code):
        AST = CodeParser(code, gold_code)
        RES = SimilarityCalculator(AST.seqA, AST.seqB, 1, 1, -1 / 3)
        return RES.answer()

    @staticmethod
    def _compare_command(command, gold_command):
        return difflib.SequenceMatcher(None, command, gold_command).quick_ratio()

    @staticmethod
    def _extract_code(response: str) -> List[dict]:
        pattern = r"```(python|bash)\n(.*?)\n```"
        code = None
        for match in re.finditer(pattern, response, re.DOTALL):
            if code is None:
                code = []
            code.append({"language": match.group(1), "code": match.group(2)})
        return code

    def tool_call(self, tool_calls: Dict):
        self.json["tools"] = tool_calls

    def user_message(self, rounds: int, message: str):
        self.json["rounds"] = rounds
        self.json["user"] = message

    def assistant_message(self, message: str):
        self.json["assistant"] = message
        self.compare_step(message, self.gold[self.json["round"]])
        self.content.append(self.json.copy())
        self.json.clear()

    def finish(self, reason: str):
        self.finish_reason = reason
        self.write_to_file()

    def code(self, language, code):
        self.json['code'] = {"language": language, "code": code}


class GlobalLogger:
    def __init__(self):
        self.analysis = []
        self.python_code = []
        self.bash_code = []
        self.no_code = []
        self.error_python = []
        self.error_bash = []
        self.partially_solved = []
        self.solved = []
        self.unsolved = []
        self.unknown = []
        self.exception = []

    def append_analysis(self, challenge: str):
        self.analysis.append(challenge)

    def append_python_code(self, challenge: str):
        self.python_code.append(challenge)

    def append_bash_code(self, challenge: str):
        self.bash_code.append(challenge)

    def append_no_code(self, challenge: str):
        self.no_code.append(challenge)

    def append_error_python(self, challenge: str):
        self.error_python.append(challenge)

    def append_error_bash(self, challenge: str):
        self.error_bash.append(challenge)

    def append_partially_solved(self, challenge: str):
        self.partially_solved.append(challenge)

    def append_solved(self, challenge: str):
        self.solved.append(challenge)

    def append_unsolved(self, challenge: str):
        self.unsolved.append(challenge)

    def append_unknown(self, challenge: str):
        self.unknown.append(challenge)

    def append_exception(self, challenge: str, exception: str):
        self.exception.append({challenge: exception})

    def write_to_file(self, file: Union[str, Path]):
        data = {
            "analysis": self.analysis,
            "python_code": self.python_code,
            "bash_code": self.bash_code,
            "no_code": self.no_code,
            "error_python": self.error_python,
            "error_bash": self.error_bash,
            "partially_solved": self.partially_solved,
            "solved": self.solved,
            "unsolved": self.unsolved,
            "unknown": self.unknown,
            "exception": self.exception,
        }
        if isinstance(file, str):
            file = Path(file)
        with open(os.path.abspath(file), "w") as f:
            json.dump(data, f, indent=4)
