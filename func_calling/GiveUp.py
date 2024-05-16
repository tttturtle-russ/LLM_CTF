from typing import Dict, Optional, Type
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun

from Env import CTFEnv

class GiveUpException(Exception):
    pass


class GiveUpInput(BaseModel):
    confirm: bool = Field(description="a boolean flag to confirm that you want to give up", default=False)


class GiveUp(BaseTool):
    name = "give_up"
    description = "Give up on the challenge"
    args_schema: Type[BaseModel] = GiveUpInput

    @staticmethod
    def handler(output) -> Dict:
        if output['give up'] is True:
            raise GiveUpException()
        else:
            return {"error": output['error']['message']}

    def _run(
            self,
            confirm: bool = False,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict:
        if not confirm:
            return {
                "error": {
                    "message": "You must confirm that you want to give up",
                    "tool": "give_up"
                }
            }
        return {"give_up": True}


GIVEUPTOOLS = [GiveUp()]
