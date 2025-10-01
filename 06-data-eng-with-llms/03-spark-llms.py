%pip install transformers
%pip install outlines

# -----------------------
# Databricks throws an error saying it already has spark runnig, don't know if it's true for all workspaces

# from pyspark.sql import SparkSession

# spark = SparkSession.builder \
#     .appName("ReviewsClassifier") \
#     .master("local[*]") \
#     .getOrCreate()

# spark


# ------------------------

reviews = [
    (1, "This is absolutely delightful!"),
    (2, "This was the worst hotel I've ever seen"),
    (3, "Great location but the rooms were dirty."),
    (4, "Staff were friendly and helpful."),
    (5, "Mediocre breakfast, but I'd stay again."),
]
df = spark.createDataFrame(
    reviews,
    ["review_id", "review"]
)
display(df)

# ------------------------
%pip install torch

import torch
import json
import outlines
import transformers

model_name = "microsoft/Phi-3-mini-4k-instruct"


from huggingface_hub import login

login(token="hf_...")

model = outlines.from_transformers(
    transformers.AutoModelForCausalLM.from_pretrained(model_name),
    transformers.AutoTokenizer.from_pretrained(model_name)
)


# ------------------------------------------
#Removed UDF approach since it was too slow and wouldn't work with a free workspace

import torch
import outlines
import transformers
from pydantic import BaseModel
from enum import Enum
from pyspark.sql import Row
import json


class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"

class Classification(BaseModel):
    sentiment: Sentiment

generator = outlines.Generator(model, Classification)

def classify_reviews(reviews):
    results = []
    for review in reviews:
        prompt = (
            "Classify the following customer review as positive or negative.\n\n"
            f"Review:\n{review}\n"
        )
        output = generator(prompt)
        parsed = json.loads(output)
        results.append(parsed["sentiment"])
    return results

# ------------------------------------------

rows = df.select("review_id", "review").collect()

reviews = [row["review"] for row in rows]

sentiments = classify_reviews(reviews)

results_df = spark.createDataFrame(
    [Row(review_id=row["review_id"], review=row["review"], sentiment=sent)
     for row, sent in zip(rows, sentiments)]
)
display(results_df)