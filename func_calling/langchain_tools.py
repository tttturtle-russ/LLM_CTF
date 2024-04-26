import json
import tempfile
from pathlib import Path
from typing import Optional, Type, Dict
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain.tools.render import render_text_description_and_args
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.prompts import ChatPromptTemplate
import subprocess

from tools import GiveUpException

SCRIPT_DIR = Path(__file__).parent.resolve()
GHIDRA = SCRIPT_DIR / 'ghidra_11.0_PUBLIC/support/analyzeHeadless'


class RunCommandInput(BaseModel):
    command: str = Field(description="Command to run")
    timeout: Optional[int] = Field(description="the maximum number of seconds to run the command (defaults to 10)",
                                   default=10)


class RunCommand(BaseTool):
    name = "run_command"
    description = "Execute a command in an Ubuntu container (persistent across calls)"
    args_schema: Type[BaseModel] = RunCommandInput

    def start_docker(self):
        if self.volume:
            volumes = ['-v', f'{self.volume}:/home/ctfplayer/ctf_files']
        else:
            volumes = []
        subprocess.run(
            ['docker', 'run'] + \
            volumes + \
            ['--network', self.network] + \
            ['--platform', 'linux/amd64', '-d', '--rm'] + \
            ['--name', self.container_name, self.container_image],
            check=True, capture_output=True,
        )

    @staticmethod
    def _clean(text):
        if text is None:
            return None
        return text.decode('utf-8', errors='backslashreplace').replace('\r\n', '\n')

    def _run(self, command, timeout: Optional[int] = 10,
             run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict:
        self.start_docker()
        try:
            p = subprocess.run(
                ['docker', 'exec', self.container_name, 'bash', '-c', command],
                timeout=timeout, check=True, capture_output=True,
            )
            out = self._clean(p.stdout)
            err = self._clean(p.stderr)
            if p.returncode != 0:
                return {"stdout": out, "stderr": err, "returncode": p.returncode, "timed_out": False, "error": {
                    "message": f"Command failed with return code {p.returncode} and showed the following error: {err}",
                    "tool": "run_command"
                }}
            return {"stdout": out, "stderr": err, "returncode": p.returncode, "timed_out": False}
        except subprocess.TimeoutExpired as e:
            out = self._clean(e.stdout)
            err = self._clean(e.stderr)
            return {"stdout": out, "stderr": err, "returncode": None, "timed_out": True, "error": {
                "message": f"Command timed out after {timeout} seconds",
                "tool": "run_command"
            }
                    }
        except subprocess.CalledProcessError as e:
            out = self._clean(e.stdout)
            err = self._clean(e.stderr)
            return {
                "stdout": out,
                "stderr": err,
                "returncode": e.returncode,
                "timed_out": False,
                "error": {
                    "message": f"Command failed to with returncode {e.returncode} and showed the following error: {err}",
                    "tool": "run_command"
                }
            }


class CheckFlagInput(BaseModel):
    flag: str = Field(description="the flag to check")


class CheckFlag(BaseTool):
    name = "checkflag"
    description = "Check if a flag is correct"
    args_schema: Type[BaseModel] = CheckFlagInput

    def _run(
            self,
            flag: str,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict:
        if flag is None:
            return {
                "error": {
                    "message": "No flag provided",
                    "tool": "checkflag"
                }
            }
        if flag == self.real_flag:
            self.challenge.solved = True
            return {"correct": True}
        else:
            return {"correct": False}


class CreateFileInput(BaseModel):
    path: str = Field(
        description="path where the file should be created; relative paths will be relative to /home/ctfplayer/")
    contents: str = Field(description="contents of the file")
    decode_escapes: Optional[bool] = Field(description="whether to decode escape sequences in the contents",
                                           default=False)


class CreateFile(BaseTool):
    name = "createfile"
    description = "create a file in the container with the given contents"
    args_schema: Type[BaseModel] = CreateFileInput

    def _run(
            self,
            path: str,
            contents: str,
            decode_escapes: Optional[bool] = False,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict:
        if path is None:
            return {
                "error": {
                    "message": "No path provided",
                    "tool": "createfile"
                }
            }
        if contents is None:
            return {
                "error": {
                    "message": "No contents provided",
                    "tool": "createfile"
                }
            }
        if decode_escapes is None:
            decode_escapes = False
        return self.createfile(path, contents, decode_escapes)

    @staticmethod
    def _expanduser(path, home='/home/ctfplayer'):
        """Expand ~ and ~user constructs in the given path"""
        strpath = str(path)
        if strpath.startswith('~'):
            strpath = strpath.replace('~', home, 1)
        return Path(strpath)

    def createfile(self, path, contents, decode_escapes=False):
        if decode_escapes:
            # Decode escape sequences to get a bytes object
            try:
                contents = bytes(contents, 'utf-8').decode('unicode_escape').encode('latin-1')
            except UnicodeDecodeError as e:
                return {
                    "error": {
                        "message": f"Invalid escape sequence in contents: {e}",
                        "tool": "createfile"
                    }
                }

        else:
            contents = contents.encode()
        path = Path(path)
        path = self._expanduser(path)
        if not path.is_absolute():
            path = Path('/home/ctfplayer') / path
        path = str(path)
        with tempfile.NamedTemporaryFile(mode='wb') as f:
            f.write(contents)
            f.flush()
            tmpfile = f.name
            # Copy the file into the container
            try:
                subprocess.run(
                    ['docker', 'cp', tmpfile, f'{self.container_name}:{path}'],
                    check=True, capture_output=True,
                )
                # Set ownership to ctfplayer
                subprocess.run(
                    ['docker', 'exec', '--user=root', '-it', self.container_name, 'chown', 'ctfplayer:ctfplayer', path],
                    check=True, capture_output=True,
                )
                return {"success": True, "path": path}
            except subprocess.CalledProcessError as e:
                return {
                    "error": {
                        "message": f"Error copying file into container: {e.stderr.decode('utf-8', errors='backslashreplace')}",
                        "tool": "createfile"
                    }
                }


class DecompileInput(BaseModel):
    binary: str = Field(description="the binary to decompile")
    function: str = Field(description="the function to decompile", default="main")


class Decompile(BaseTool):
    name = "decompile_function"
    description = "Decompile a function from a binary using Ghidra"
    args_schema: Type[BaseModel] = DecompileInput

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
            decomp_output = SCRIPT_DIR / f"decomp/{self.challenge.category}/{self.challenge.chaldir.name}/{basename}.decomp.json"
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
        binary_paths = self.challenge.chaldir.glob(f'**/{binary}')
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
        disasm_output = SCRIPT_DIR / f"decomp/{self.challenge.category}/{self.challenge.chaldir.name}/{basename}.disas.json"

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
        binary_paths = self.challenge.chaldir.glob(f'**/{binary}')
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


class GiveUpInput(BaseModel):
    confirm: bool = Field(description="a boolean flag to confirm that you want to give up", default=False)


class GiveUp(BaseTool):
    name = "give_up"
    description = "Give up on the challenge"
    args_schema: Type[BaseModel] = GiveUpInput

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
        raise GiveUpException()


class TestInput(BaseModel):
    num1: int = Field(description="a number", default=1)
    num2: int = Field(description="another number", default=2)


class TestTool(BaseTool):
    name = "add"
    description = "add two numbers together"
    args_schema: Type[BaseModel] = TestInput

    def _run(
            self,
            num1: int = 1,
            num2: int = 2,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict:
        return {"sum": num1 + num2}


DEFAULT_TOOLSET = [RunCommand(), CheckFlag(), CreateFile(), Decompile(), Disassemble(), GiveUp(), TestTool()]

# Predefined sets of tools for different categories
TOOLSETS = {
    # No binaries in the misc, forensics, or crypto categories
    "crypto": [RunCommand, CheckFlag, CreateFile, GiveUp],
    "misc": [RunCommand, CheckFlag, CreateFile, GiveUp],
    "forensics": [RunCommand, CheckFlag, CreateFile, GiveUp],
    "default": DEFAULT_TOOLSET,
}

rendered_tools = render_text_description_and_args(DEFAULT_TOOLSET)

system_prompt = f"""You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

{rendered_tools}

Given the user input, return the name and input of the tool to use. Return your response as a JSON blob with 'name' and 'arguments' keys."""

prompt = ChatPromptTemplate.from_messages(
    [("user", system_prompt + "{input}")]
)
