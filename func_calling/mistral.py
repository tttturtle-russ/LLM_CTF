from typing import Optional, List, Any
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel, LanguageModelInput
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.prompt_values import PromptValue
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.llms.base import LLM
from rich import print
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


class MistralAgent(BaseChatModel):
    name = "Mistral"
    model_name = "/home/haoyang/Mistral-7B-Instruct-v0.2"
    client = OpenAI(
        api_key="na",
        base_url="http://localhost:8000/v1"
    )

    @staticmethod
    def convert_messages(messages: List[BaseMessage]):
        return [
            {"role": "user", "content": message.content}
            if isinstance(message, HumanMessage)
            else {"role": "assistant", "content": message.content}
            for message in messages
        ]

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        print(messages)
        last_message = messages[-1]
        print(last_message.content)
        template_message = self.convert_messages(messages)
        resp = self.client.chat.completions.create(
            messages=template_message,
            model=self.model_name,
        )
        print(resp)
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content=resp.choices[0].message.content,
                        additional_kwargs={},  # Used to add additional payload (e.g., function calling request)
                        response_metadata={  # Use for response metadata
                            "time_in_seconds": 3,
                        },
                    )
                )
            ]
        )

    @property
    def _llm_type(self) -> str:
        return "Mistral-7B-Instruct-v0.2"


test = MistralAgent()

print(test.invoke("write me a quick sort algorithm in C").content)
