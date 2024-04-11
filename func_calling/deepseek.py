from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class DeepSeek:
    def __init__(self):
        self.id = "deepseek-ai/deepseek-coder-6.7b-instruct"
        self.model = AutoModelForCausalLM.from_pretrained(
            self.id,
            torch_dtype=torch.bfloat16,
            device_map='auto'
        ).cuda()
        self.tokenizer = AutoTokenizer.from_pretrained(self.id)

    def generate(self):