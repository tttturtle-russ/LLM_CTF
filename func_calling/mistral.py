from typing import Optional, List, Any
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.tools import BaseTool
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.llms.base import LLM
from langchain.agents import load_tools, initialize_agent, AgentType
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
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map='auto',
            use_cache=True,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
            top_k=5,
            num_return_sequences=1,
            max_length=3200,
            do_sample=True,
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

    @property
    def _llm_type(self) -> str:
        return "Mistral-7B-Instruct-v0.2"



class MistralAgent:
    def __init__(self, llm: Mistral, tool_choice: List[BaseTool]):
        self.model = llm
        self.tools = tool_choice
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.model,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def generate(self, prompt):
        return self.agent.run(prompt)
