from typing import List, Any

import openai
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_tools import *

from ctflogging import status


class DeepSeekAgent(BaseChatModel):
    name = "DeepSeek"
    model_name = "/home/haoyang/deepseek-coder-6.7b-base"

    _messages = []

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
        resp.choices[0].message.content.replace("\\", "")
        self._messages.append({"role": "assistant", "content": resp.choices[0].message.content})
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
        return "deepseek-coder-6.7b-base"
