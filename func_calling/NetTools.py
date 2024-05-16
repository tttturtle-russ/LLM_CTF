from typing import Type, Optional, Dict, List, Union

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from Env import CTFEnv


class ListenCommandToolInput(BaseModel):
    command: str = Field(description="The command to use to listen for incoming connections")


class ListenCommandTool(BaseTool):
    name = "net_listen"
    description = "Listen on a port for incoming connections"
    args_schema: Type[BaseModel] = ListenCommandToolInput
    env: CTFEnv

    @staticmethod
    def handler(output) -> Dict:
        if 'error' in output:
            error = output['error']
            return {"error": f"Failed to listen with error: {error['message']}"}
        else:
            return {
                "stdout": output["stdout"],
                "stderr": output["stderr"],
                "returncode": output["returncode"],
                "outfile": "net.out"
            }

    def _run(
            self,
            command: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        p = self.env.exec(command)
        if p is None:
            return {
                "error": {
                    "message": "Internal error",
                    "tool": "net_listen"
                }
            }
        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "net_listen"
                }
            }
        return {
            "stdout": p.stdout.decode(),
            "stderr": p.stderr.decode(),
            "returncode": p.returncode,
            "outfile": "net.out"
        }

    def _run_nc(
            self,
            port: int,
            options: Optional[Union[List[str], str]] = None,
            host: Optional[str] = None,
    ) -> Dict:
        """
        Run the nc command to listen on a port
        nc command should be formatted as follows:
            connect to somewhere:  nc [options] hostname port [port] ...
            listen for inbound:    nc -l -p port [options] [hostname] [port] ...
            tunnel to somewhere:   nc -L hostname:port -p port [options]
        """
        command_with_options = f"nc -l -p {port}"
        if options is not None:
            command_with_options += f" {options}"
        if host is not None:
            command_with_options += f" {host}"
        p = self.env.exec(command_with_options)
        if p is None:
            return {
                "error": {
                    "message": "Internal error",
                    "tool": "net_listen"
                }
            }
        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "net_listen"
                }
            }
        return {
            "stdout": p.stdout.decode(),
            "stderr": p.stderr.decode(),
            "returncode": p.returncode,
            "outfile": "nc.out"
        }


class RequestCommandToolInput(BaseModel):
    command: str = Field(description="The command to use to make a request")


class RequestCommandTool(BaseTool):
    name = "net_request"
    description = "Make a request to a server"
    args_schema: Type[BaseModel] = RequestCommandToolInput
    env: CTFEnv

    def _run(
            self,
            command: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        p = self.env.exec(command)
        if p is None:
            return {
                "error": {
                    "message": "Internal error",
                    "tool": "net_request"
                }
            }
        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "net_request"
                }
            }
        return {
            "stdout": p.stdout.decode(),
            "stderr": p.stderr.decode(),
            "returncode": p.returncode,
        }

    @staticmethod
    def handler(output) -> Dict:
        if 'error' in output:
            error = output['error']
            return {"error": f"Failed to make request with error: {error['message']}"}
        else:
            return {
                "stdout": output["stdout"],
                "stderr": output["stderr"],
                "returncode": output["returncode"],
            }

class ScanCommandToolInput(BaseModel):
    command: str = Field(description="The command to use to scan for open ports")


class ScanCommandTool(BaseTool):
    name = "net_scan"
    description = "Scan for open ports on a host"
    args_schema: Type[BaseModel] = ScanCommandToolInput
    env: CTFEnv

    def _run(
            self,
            command: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        p = self.env.exec(command)
        if p is None:
            return {
                "error": {
                    "message": "Internal error",
                    "tool": "net_scan"
                }
            }
        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "net_scan"
                }
            }
        return {
            "stdout": p.stdout.decode(),
            "stderr": p.stderr.decode(),
            "returncode": p.returncode,
        }

    @staticmethod
    def handler(output) -> Dict:
        if 'error' in output:
            error = output['error']
            return {"error": f"Failed to scan with error: {error['message']}"}
        else:
            return {
                "stdout": output["stdout"],
                "stderr": output["stderr"],
                "returncode": output["returncode"],
            }

NETTOOLS = [ListenCommandTool(), RequestCommandTool(), ScanCommandTool()]