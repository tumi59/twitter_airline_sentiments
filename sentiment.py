from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


def get_sentimnet(text):
    model_name = 'distilbert-base-uncased-finetuned-sst-2-english'
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
        sentiment = 'positive'
    else:
        sentiment = 'unknown'

    # print(f'The sentiment of the text is {sentiment}.')
    return sentiment
