import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class DeepSeek:

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            device_map='auto'
        ).cuda()
        self.prompts = []

    def generate(self, prompt, tempurature=1.0, top_p=1.0, append_msg=""):
        self.prompts.append({"role": "user", "content": f"{prompt}\n{append_msg}"})
        inputs = self.tokenizer.apply_chat_template(
            self.prompts,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to("cuda")

        outputs = self.model.generate(
            inputs,
            max_new_tokens=512,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            tempurature=tempurature,
            top_p=top_p,
            do_sample=False
        )

        resp = self.tokenizer.decode(outputs.squeeze(), skip_special_tokens=True)
        self.prompts.append({"role": "assistant", "content": resp})

        return resp
