from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Dict, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun

from func_calling.Env import CTFEnv


class CheckFlagInput(BaseModel):
    flag: str = Field(description="the flag to check")


class CheckFlag(BaseTool):
    name = "check_flag"
    description = "Check if a flag is correct"
    args_schema: Type[BaseModel] = CheckFlagInput

    real_flag: str = None
    env:CTFEnv

    @staticmethod
    def handler(output) -> Dict:
        if 'correct' in output:
            if output['correct'] is True:
                return {"correct": True}
            else:
                return {"correct": False}
        else:
            error = output['error']
            return {"error": f"{error['tool']} failed with error: {error['message']}"}

    def _run(
            self,
            flag: str = None,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict:
        self.env.log.tool_call()
        if flag is None:
            return {
                "error": {
                    "message": "No flag provided",
                    "tool": "check_flag"
                }
            }
        if flag == self.real_flag:
            self.challenge.solved = True
            return {"correct": True}
        else:
            return {"correct": False}

CHECKFLAGTOOLS = [CheckFlag()]