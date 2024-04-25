from typing import Optional, List, Any
from langchain_core.callbacks import CallbackManagerForLLMRun
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain.llms.base import LLM
import torch


class Mistral(LLM):
    def __init__(self):
        super().__init__()
        self.model_id = "mistralai/Mistral-7B-Instruct-v0.2"
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.id,
            device_map='auto',
            torch_dtype=torch.float16,
            load_in_8bit=False
        )
        self.messages = []

    def _call(self, prompt: str, stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> str:
        self.messages.append(prompt)
        inputs = self.tokenizer.apply_chat_template(self.messages, return_tensors="pt")
        outputs = self.model.generate(
            inputs,
            max_new_tokens=500,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            temperature=1.0,
            top_p=1.0
        )
        resp = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        self.messages.append()
        tool_calls = self._extract_tool_calls(resp)


    @property
    def _llm_type(self) -> str:
        return "Mistral-7B-Instruct-v0.2"

    def _extract_tool_calls(self, response):
        tool_calls = []

