from typing import Dict, Optional, Type
import json
import subprocess
import tempfile
from pathlib import Path
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun

from Env import CTFEnv

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
    env: CTFEnv

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
    env: CTFEnv

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


REVERSETOOLS = [Decompile(), Disassemble()]
