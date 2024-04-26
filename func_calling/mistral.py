from operator import itemgetter
from typing import List, Any

import openai
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel, LanguageModelInput
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain.tools.render import render_text_description
from langchain_core.runnables import RunnablePassthrough
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.llms.base import LLM
from rich import print
from langchain_tools import *
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

    # client = OpenAI(
    #     api_key="na",
    #     base_url="http://localhost:8000/v1"
    # )

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
        openai.base_url = "http://localhost:8000/v1/"
        openai.api_key = "na"
        template_message = self.convert_messages(messages)
        resp = openai.chat.completions.create(
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


model = MistralAgent()
tools = [RunCommand(), CheckFlag(), CreateFile(), Disassemble(), Decompile(), TestTool()]
print(str(tools[1].args))
rendered_tools = render_text_description_and_args(tools).replace("{", "{{").replace("}", "}}")

print(rendered_tools)

system_prompt = f"""You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

{rendered_tools}

Given the user input, return the name and input of the tool to use. Return your response as a JSON blob with 'name' and 'arguments' keys, arguments should be an object instead a list."""


def tool_chain(model_output):
    tool_map = {tool.name: tool for tool in tools}
    chosen_tool = tool_map[model_output["name"]]
    return itemgetter("arguments") | chosen_tool


prompt = ChatPromptTemplate.from_messages(
    [("user", system_prompt + "{input}")]
)

print(system_prompt)

chain = prompt | model | JsonOutputParser() | RunnablePassthrough.assign(output=tool_chain)

print(chain.invoke({"input": "I want to give up and I'm confirmed"}))
