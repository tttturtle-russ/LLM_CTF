from typing import Type, Optional, Dict, List, Union

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from Env import CTFEnv


class KillProcessInput(BaseModel):
    command: str = Field(description="The command to use to kill a process")


class KillProcess(BaseTool):
    name = "kill_process"
    description = "Kill a process using the kill command"
    args_schema: Type[BaseModel] = KillProcessInput
    env: CTFEnv

    @staticmethod
    def handler(output) -> Dict:
        if "error" in output:
            return {"error": output["error"]["message"]}
        return {"status": "success"}

    def _run(
            self,
            command: str,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict:
        p = self.env.exec(command)
        if p is None:
            return {
                "error": {
                    "message": "Internal error",
                    "tool": "kill_process"
                }
            }

        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "kill_process"
                }
            }

        return {
            "status": "success"
        }


PROCESSTOOLS = [KillProcess()]
