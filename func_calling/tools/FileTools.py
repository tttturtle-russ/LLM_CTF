import subprocess
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import Field, BaseModel
from langchain.tools import BaseTool
from typing import Dict, Optional, Type, Union, List
from enum import Enum

class ReadFileCommand(str, Enum):
    """
    Enum for the read_file command
    These command types can read both ascii and binary files
    """
    CAT = "cat"
    HEAD = "head"
    TAIL = "tail"
    HEXDUMP = "hexdump"
    OBJDUMP = "objdump"
    STRINGS = "strings"


class ReadFileInput(BaseModel):
    command: ReadFileCommand = Field(description="the command to use to read the file")
    arguments: Optional[Union[str, List[str]]] = Field(description="arguments to pass to the command", default=None)
    path: str = Field(description="path to the file to read")


class ReadFile(BaseTool):
    name = "read_file"
    description = "Read the contents of a file"
    args_schema: Type[BaseModel] = ReadFileInput

    def readfile(
            self,
            command: ReadFileCommand,
            arguments: Optional[List[str]],
            path: str
    ) -> Dict:
        p = subprocess.run([command, *arguments, path], capture_output=True)
        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "read_file"
                }
            }


    def _run(
            self,
            command: ReadFileCommand,
            arguments: Optional[Union[str, List[str]]],
            path: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        if path is None:
            return {
                "error": {
                    "message": "No path provided",
                    "tool": "read_file"
                }
            }
        if arguments is None:
            return self.readfile(command, [], path)
        elif isinstance(arguments, str):
            return self.readfile(command, [arguments], path)
        return self.readfile(command,arguments,path)
