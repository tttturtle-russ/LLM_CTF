import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class LocalMixtral:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            # run on multi GPUs
            device_map='auto',
            torch_dtype=torch.float16,
            load_in_8bit=False
        )
        self.prompts = []

    def generate(self, prompt, temperature=1.0, top_p=1.0, append_msg=""):
        self.prompts.append({"role": "user", "content": f"{prompt}\n{append_msg}"})
        inputs = (self.tokenizer.
                  apply_chat_template(self.prompts, return_tensors="pt").
                  to(torch.cuda.current_device()))
        outputs = self.model.generate(
            inputs,
            max_new_tokens=500,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            temperature=temperature,
            top_p=top_p
        )
        resp = self.tokenizer.decode(outputs.squeeze(), skip_special_tokens=True)
        self.prompts.append({"role": "assistant", "content": resp})
        return resp
