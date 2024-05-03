from typing import Type, Optional, Dict, List, Union

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from ..Env import CTFEnv


class InstallPkgInput(BaseModel):
    command: str = Field(description="The command to use to install a package")


class InstallPkg(BaseTool):
    name = "install_pkg"
    description = "Install a package using pip or apt-get"
    args_schema: Type[BaseModel] = InstallPkgInput
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
                    "tool": "install_pkg"
                }
            }

        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "install_pkg"
                }
            }

        return {
            "status": "success"
        }


PKGTOOLS = [InstallPkg()]
