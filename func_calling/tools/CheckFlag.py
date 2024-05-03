from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Dict, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun

class CheckFlagInput(BaseModel):
    flag: str = Field(description="the flag to check")


class CheckFlag(BaseTool):
    name = "check_flag"
    description = "Check if a flag is correct"
    args_schema: Type[BaseModel] = CheckFlagInput

    real_flag: str = None

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