from operator import itemgetter
from typing import List, Any

import openai
from langchain.chains.llm import LLMChain
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser, XMLOutputParser
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import MessagesPlaceholder
from rich import print
from langchain_tools import *

from ctflogging import status

openai.base_url = "http://localhost:8000/v1/"
openai.api_key = "na"


def tool_chain(model_output, tools):
    tool_map = {tool.name: tool for tool in tools}

    def chain(_model_output):
        chosen_tool = tool_map[_model_output["name"]]
        return itemgetter("arguments") | chosen_tool

    return chain


class MistralAgent(BaseChatModel):
    name = "Mistral"
    model_name = "/home/haoyang/Mistral-7B-Instruct-v0.2"

    _messages = []

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
        status.user_message(messages[-1].content)
        self._messages.append(HumanMessage(content=messages[-1].content))
        # template_message = self.convert_messages(self._messages)
        resp = openai.chat.completions.create(
            messages=self._message,
            model=self.model_name,
        )
        self._messages.append(AIMessage(content=resp.choices[0].message.content))
        status.assistant_message(resp.choices[0].message.content)
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
