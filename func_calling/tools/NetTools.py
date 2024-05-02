from enum import Enum
from typing import Type, Optional, Dict, List, Union

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from ..Env import CTFEnv


class ListenCommand(str, Enum):
    NC = "nc"
    TCPDUMP = "tcpdump"
    TSHARK = "tshark"


class ListenCommandToolInput(BaseModel):
    command: ListenCommand = Field(description="The command to use to listen for incoming connections")
    port: int = Field(description="The port to listen on")
    options: Optional[Union[List[str], str]] = Field(description="Options to pass to the command", default=None)
    host: Optional[str] = Field(description="The host to listen on", default="127.0.0.1")


class ListenCommandTool(BaseTool):
    name = "net_listen"
    description = "Listen on a port for incoming connections"
    args_schema: Type[BaseModel] = ListenCommandToolInput
    env: CTFEnv

    def _run(
            self,
            command: ListenCommand,
            port: int,
            options: Optional[Union[List[str], str]] = None,
            host: Optional[str] = None,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        if command == ListenCommand.NC:
            return self._run_nc(port, options, host)
        elif command == ListenCommand.TCPDUMP:
            return self._run_tcpdump(host, port, run_manager)
        elif command == ListenCommand.TSHARK:
            return self._run_tshark(host, port, run_manager)
        else:
            raise ValueError(f"Unknown command {command}")

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
        command_with_options += "> "
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
