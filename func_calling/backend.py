from fastapi import FastAPI, Request
import torch
import argparse
from .mistral import Mistral
from .deepseek import DeepSeek

parser = argparse.ArgumentParser(
    description="Start API server",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument("-M", "--model", required=True)

args = parser.parse_args()
app = FastAPI()
if args.model == "mistral":
    model = Mistral()
elif args.model == "deepseek":
    model = DeepSeek()
else:
    raise ValueError(f"Unknown model {args.model}")


@app.post("/v1/chat/completions")
async def chat(request: Request):
    data = await request.json()
    if "messages" not in data:
        return {"error": "messages field is required"}
    messages = data.get("messages", [])
    tools = data.get("tools", [])
    if model is None:
        return {"error": "model field is required"}
    tool_choice = data.get("tool_choice", None)
    if tool_choice is None:
        return {"error": "tool_choice field is required"}
    response = model.generate(messages, tools, tool_choice)
    return response