import json
import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from typing import Dict, Optional, Type, Union, List

class DockerHelper:
    def __init__(self, chal, container):
        self.container = container
        self.chal = chal

    def exec(self, command_with_arguments):
        return subprocess.run(
            ['docker', 'exec', self.container] + \
            ['--user', 'ctfbench'] + \
            ['bash', '-c', command_with_arguments],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

SCRIPT_DIR = Path(__file__).parent.parent.resolve()
GHIDRA = SCRIPT_DIR / 'ghidra_11.0_PUBLIC/support/analyzeHeadless'


class DecompileInput(BaseModel):
    binary: str = Field(description="the binary to decompile")
    function: str = Field(description="the function to decompile", default="main")


class Decompile(BaseTool):
    name = "decompile_function"
    description = "Decompile a function from a binary using Ghidra"
    args_schema: Type[BaseModel] = DecompileInput

    _decomp_cache: Dict = {}
    env: DockerHelper

    @staticmethod
    def handler(output) -> Dict:
        if 'decompilation' in output:
            return {"decompilation": output['decompilation']}
        else:
            error = output['error']
            return {"error": f"{error['tool']} failed with error: {error['message']}"}

    def _run(
            self,
            binary: str,
            function: str = "main",
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict:
        if binary is None:
            return {
                "error": {
                    "message": f"No {binary} provided",
                    "tool": "decompile_function"
                }
            }
        if function is None:
            function = "main"
        return self.decompile(binary, function)

    def decompile(self, binary, function):
        # Look for the decompilation output in "decomp"
        basename = Path(binary).name
        if basename not in self._decomp_cache:
            self._decomp_cache[basename] = {}
            decomp_output = SCRIPT_DIR / f"decomp/{self.env.chal.category}/{self.env.chal.chaldir.name}/{basename}.decomp.json"
            if decomp_output.exists():
                self._decomp_cache[basename] = json.loads(decomp_output.read_text())
            else:
                if not self.run_ghidra(basename, decomp_output):
                    return {
                        "error": {
                            "message": f"Decompilation for {binary} not available",
                            "tool": "decompile_function"
                        }
                    }
                self._decomp_cache[basename] = json.loads(decomp_output.read_text())
        if function not in self._decomp_cache[basename]:
            # If they're trying to find main, try again with _start instead
            if function == "main":
                return self.decompile(binary, "_start")
            else:
                return {
                    "error": {
                        "message": f"Function {function} not found in {binary}",
                        "tool": "decompile_function"
                    }
                }
        return {"decompilation": self._decomp_cache[basename][function]}

    def run_ghidra(self, binary, output):
        binary_paths = self.env.chal.chaldir.glob(f'**/{binary}')
        real_binary = next(binary_paths, None)
        if not real_binary or not real_binary.exists():
            return False
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            subprocess.run(
                [GHIDRA, tmpdir, "DummyProj", "-scriptpath", SCRIPT_DIR / 'ghidra_scripts',
                 "-import", real_binary, "-postscript", "DecompileToJson.java", output],
                check=False, capture_output=True,
            )
            return output.exists()


class DisassembleInput(BaseModel):
    binary: str = Field(description="the binary to disassemble")
    function: str = Field(description="the function to disassemble", default="main")


class Disassemble(BaseTool):
    name = "disassemble_function"
    description = "Disassemble a function from a binary using Ghidra"
    args_schema: Type[BaseModel] = DisassembleInput

    _disasm_cache: Dict = {}
    env: DockerHelper

    @staticmethod
    def handler(output) -> Dict:
        if 'disassembly' in output:
            return {"disassembly": output['disassembly']}
        else:
            error = output['error']
            return {"error": f"{error['tool']} failed with error: {error['message']}"}

    def _run(
            self,
            binary: str,
            function: str = "main",
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict:
        if function is None:
            function = "main"
        if binary is None:
            return {
                "error": {
                    "message": "No binary provided",
                    "tool": "disassemble_function"
                }
            }
        return self.disassemble(binary, function)

    def disassemble(self, binary, function):
        # Look for the disassembly output in "decomp"
        basename = Path(binary).name
        disasm_output = SCRIPT_DIR / f"decomp/{self.env.chal.category}/{self.env.chal.chaldir.name}/{basename}.disas.json"

        if basename not in self._disasm_cache:
            if disasm_output.exists():
                self._disasm_cache[basename] = json.loads(disasm_output.read_text())
            else:
                if not self.run_ghidra(basename, disasm_output):
                    return {
                        "error": {
                            "message": f"Disassembly for {binary} not available",
                            "tool": "disassemble_function"
                        }
                    }
                self._disasm_cache[basename] = json.loads(disasm_output.read_text())

        if function not in self._disasm_cache[basename]:
            # If they're trying to find main, try again with _start instead
            if function == "main":
                return self.disassemble(binary, "_start")
            else:
                return {
                    "error": {
                        "message": f"Function {function} not found in {binary}",
                        "tool": "disassemble_function"
                    }
                }
        return {"disassembly": self._disasm_cache[basename][function]}

    def run_ghidra(self, binary, output):
        binary_paths = self.env.chal.chaldir.glob(f'**/{binary}')
        real_binary = next(binary_paths, None)
        if not real_binary or not real_binary.exists():
            return False
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            subprocess.run(
                [GHIDRA, tmpdir, "DummyProj", "-scriptpath", SCRIPT_DIR / 'ghidra_scripts',
                 "-import", real_binary, "-postscript", "DisassembleToJson.java", output],
                check=False, capture_output=True,
            )
            return output.exists()


class ListenCommandToolInput(BaseModel):
    command: str = Field(description="The command to use to listen for incoming connections")


class ListenCommandTool(BaseTool):
    name = "net_listen"
    description = "Listen on a port for incoming connections"
    args_schema: Type[BaseModel] = ListenCommandToolInput
    env: DockerHelper

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
    env: DockerHelper

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
    env: DockerHelper

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


class InstallPkgInput(BaseModel):
    command: str = Field(description="The command to use to install a package")


class InstallPkg(BaseTool):
    name = "install_pkg"
    description = "Install a package using pip or apt-get"
    args_schema: Type[BaseModel] = InstallPkgInput
    env: DockerHelper

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


class KillProcessInput(BaseModel):
    command: str = Field(description="The command to use to kill a process")


class KillProcess(BaseTool):
    name = "kill_process"
    description = "Kill a process using the kill command"
    args_schema: Type[BaseModel] = KillProcessInput
    env: DockerHelper

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
    env: DockerHelper

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
    env: DockerHelper

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
    env: DockerHelper

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
    env: DockerHelper

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


class CheckFlagInput(BaseModel):
    flag: str = Field(description="the flag to check")


class CheckFlag(BaseTool):
    name = "check_flag"
    description = "Check if a flag is correct"
    args_schema: Type[BaseModel] = CheckFlagInput

    real_flag: str = None
    env: DockerHelper

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
FILETOOLS = [ReadFile(), WriteFile(), CreateFile(), RemoveFile()]
GIVEUPTOOLS = [GiveUp()]
PROCESSTOOLS = [KillProcess()]
PKGTOOLS = [InstallPkg()]
NETTOOLS = [ListenCommandTool(), RequestCommandTool(), ScanCommandTool()]
REVERSETOOLS = [Decompile(), Disassemble()]
DEFAULT_TOOLSET = REVERSETOOLS + FILETOOLS + CHECKFLAGTOOLS + GIVEUPTOOLS + PROCESSTOOLS + PKGTOOLS + NETTOOLS

TOOLSETS = {
    "crypto": FILETOOLS + CHECKFLAGTOOLS + GIVEUPTOOLS + PKGTOOLS + PROCESSTOOLS,
    "misc": FILETOOLS + CHECKFLAGTOOLS + GIVEUPTOOLS + PROCESSTOOLS + PKGTOOLS + NETTOOLS,
    "forensics": FILETOOLS + CHECKFLAGTOOLS + GIVEUPTOOLS + PKGTOOLS + PROCESSTOOLS + NETTOOLS,
    "default": DEFAULT_TOOLSET,
}
