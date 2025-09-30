%pip install transformers
%pip install sentence-transformers
%pip install outlines
%pip install torch


from huggingface_hub import login

login(token="hf_...")


import torch
import json
import outlines
import transformers

model_name = "microsoft/Phi-3-mini-4k-instruct"


model = outlines.from_transformers(
    transformers.AutoModelForCausalLM.from_pretrained(model_name),
    transformers.AutoTokenizer.from_pretrained(model_name)
)

%pip install pydantic

import outlines
from pydantic import BaseModel
from enum import Enum

class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"


class Classification(BaseModel):
    sentiment: Sentiment

generator = outlines.Generator(model, Classification)

def classify_review(review):
    prompt = (
        "Classify the following customer review as positive or negative based on review content.\n\n"
        f"Review:\n{review}\n"
    )
    output_json = generator(prompt)
    return output_json

print(classify_review("This is absolutely delightful!"))

print(classify_review("This was the worst hotel I've ever seen"))