from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


class Mixtral:
    def __init__(self):
        self.id = "mistralai/Mistral-7B-Instruct-v0.2"
        self.model = AutoModelForCausalLM.from_pretrained(self.id)
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.id,
            device_map='auto',
            torch_dtype=torch.float16,
            load_in_8bit=False
        )

    def generate(self, messages, tools, tool_choice):
        inputs = self.tokenizer.apply_chat_template(messages, return_tensors="pt")
        outputs = self.model.generate(
            inputs,
            max_new_tokens=500,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            temperature=1.0,
            top_p=1.0
        )

        resp = self.tokenizer.decode(outputs.squeeze(), skip_special_tokens=True)
        return resp

    def _extract_tool_calls(self, response):
        tool_calls = []
