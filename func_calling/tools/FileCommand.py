from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import Field, BaseModel
from langchain.tools import BaseTool
from typing import Dict, Optional, Type, Union, List
from enum import Enum

from ..Env import CTFEnv


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


class WriteFileCommand(str, Enum):
    """
    Enum for the write_file command
    These command types can write both ascii and binary files
    """
    ECHO = "echo"
    PRINTF = "printf"


class CreateFileCommand(str, Enum):
    """
    Enum for the create_file command
    These command types can write both ascii and binary files
    """
    TOUCH = "touch"


class ReadFileInput(BaseModel):
    command: ReadFileCommand = Field(description="the command to use to read the file")
    arguments: Optional[Union[str, List[str]]] = Field(description="arguments to pass to the command", default=None)
    path: str = Field(description="path to the file to read")


class ReadFile(BaseTool):
    name = "read_file"
    description = "Read the contents of a file"
    args_schema: Type[BaseModel] = ReadFileInput
    env: CTFEnv

    def readfile(
            self,
            command: ReadFileCommand,
            arguments: Optional[List[str]],
            path: str
    ) -> Dict:
        if arguments is None:
            p = self.env.exec(f"{command} {path}")
        else:
            p = self.env.exec(f"{command} {' '.join(arguments)} {path}")
        if p is None:
            return {
                "error": {
                    "message": "Internal error",
                    "tool": "read_file"
                }
            }
        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "read_file"
                }
            }
        return {"content": p.stdout.decode()}

    @staticmethod
    def handler(output) -> Dict:
        if 'error' in output:
            return {"error": f"Failed to read file: {output['error']['message']}"}
        return {"content": output['content']}

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
        if isinstance(arguments, str):
            return self.readfile(command, [arguments], path)
        return self.readfile(command, arguments, path)


class WriteFileInput(BaseModel):
    command: WriteFileCommand = Field(description="the command to use to write the file")
    path: str = Field(description="path to the file to write")
    content: str = Field(description="content to write to the file")


class WriteFile(BaseTool):
    name = "write_file"
    description = "Write content to a file"
    args_schema: Type[BaseModel] = WriteFileInput
    env: CTFEnv


    def writefile(
            self,
            command: WriteFileCommand,
            path: str,
            content: str
    ) -> Dict:
        p = self.env.exec(f"{command} {content} > {path}")
        if p is None:
            return {
                "error": {
                    "message": "Internal error",
                    "tool": "write_file"
                }
            }
        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "write_file"
                }
            }
        return {"status": "success"}


    @staticmethod
    def handler(output) -> Dict:
        if 'error' in output:
            return {"error": f"Failed to write file: {output['error']['message']}"}
        return {"success": True}

    def _run(
            self,
            command: WriteFileCommand,
            path: str,
            content: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        if path is None:
            return {
                "error": {
                    "message": "No path provided",
                    "tool": "write_file"
                }
            }
        if content is None:
            return {
                "error": {
                    "message": "No content provided",
                    "tool": "write_file"
                }
            }
        return self.writefile(command, path, content)


class CreateFileInput(BaseModel):
    command: CreateFileCommand = Field(description="the command to use to create the file")
    path: str = Field(description="path to the file to create")


class CreateFile(BaseTool):
    name = "create_file"
    description = "Create a empty file"
    args_schema: Type[BaseModel] = CreateFileInput
    env: CTFEnv

    def createfile(
            self,
            command: CreateFileCommand,
            path: str,
    ) -> Dict:
        p = self.exec(f"{command} {path}")
        if p is None:
            return {
                "error": {
                    "message": "Internal error",
                    "tool": "create_file"
                }
            }
        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "create_file"
                }
            }
        return {"status": "success"}

    def _run(
            self,
            command: CreateFileCommand,
            path: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        if path is None:
            return {
                "error": {
                    "message": "No path provided",
                    "tool": "create_file"
                }
            }
        return self.createfile(command, path)

    @staticmethod
    def handler(output) -> Dict:
        if 'error' in output:
            return {"error": f"Failed to create file: {output['error']['message']}"}
        return {"success": True}


class RemoveFileInput(BaseModel):
    path: str = Field(description="path to the file to remove")


class RemoveFile(BaseTool):
    name = "remove_file"
    description = "Remove a file"
    args_schema: Type[BaseModel] = RemoveFileInput
    env: CTFEnv

    def removefile(
            self,
            path: str,
    ) -> Dict:
        p = self.env.exec(f"rm -rf {path}")
        if p is None:
            return {
                "error": {
                    "message": "Internal error",
                    "tool": "remove_file"
                }
            }
        if p.returncode != 0:
            return {
                "error": {
                    "message": p.stderr.decode(),
                    "tool": "remove_file"
                }
            }
        return {"status": "success"}

    def _run(
            self,
            path: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        if path is None:
            return {
                "error": {
                    "message": "No path provided",
                    "tool": "remove_file"
                }
            }
        return self.removefile(path)

    @staticmethod
    def handler(output) -> Dict:
        if 'error' in output:
            return {"error": f"Failed to remove file: {output['error']['message']}"}
        return {"success": True}

FILETOOLS = [ReadFile(), WriteFile(), CreateFile(), RemoveFile()]
