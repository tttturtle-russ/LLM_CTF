from typing import List, Any

import openai
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_tools import *
from json_repair import repair_json

from ctflogging import status

openai.base_url = "http://localhost:8000/v1/"
openai.api_key = "na"


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
        self._messages.append({"role": "user", "content": messages[-1].content})
        # template_message = self.convert_messages(self._messages)
        resp = openai.chat.completions.create(
            messages=self._messages,
            model=self.model_name,
        )
        content = repair_json(resp.choices[0].message.content)
        self._messages.append({"role": "assistant", "content": content})
        status.assistant_message(content)
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content=content,
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

    def reset(self):
        self._messages = []