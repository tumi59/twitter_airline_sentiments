from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def get_sentiment(text):
    model_name = 'cardiffnlp/twitter-roberta-base-sentiment'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)

    outputs = model(**inputs)

    logits = outputs.logits

    probs = torch.nn.functional.softmax(logits, dim=-1)
    result = torch.argmax(probs)

    if result == 0:
        sentiment = 'negative'
    elif result == 1:
        sentiment = 'neutral'
    elif result == 2:
        sentiment = 'positive'
    else:
        sentiment = 'unknown'

    return sentiment