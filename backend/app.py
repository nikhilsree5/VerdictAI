from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

app = Flask(__name__)
CORS(app)

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    print("Analyse_text")
    data = request.get_json()
    text = data.get('text', '')

    MODEL_NAME = "sangkm/go-emotions-fine-tuned-distilroberta"

    def load_model():
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        return tokenizer, model

    tokenizer, model = load_model()

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1).flatten().tolist()
    probs = [round(i * 100, 2) for i in probs]
    emo_long = ["Admiration", "Amusement", "Anger", "Annoyance", "Approval", "Caring", "Confusion", "Curiosity",
                "Desire", "Disappointment", "Disapproval", "Disgust", "Embarrassment", "Excitement", "Fear",
                "Gratitude", "Grief", "Joy", "Love", "Nervousness", "Optimism", "Pride", "Realization", "Relief",
                "Remorse", "Sadness", "Surprise", "Neutral"]
    emo_dict_long = dict(zip(emo_long, probs))
    emo = pd.DataFrame(emo_dict_long, index=['Emotions']).T

    emo = emo.reset_index()
    emo.columns = ["Emotion", "Percentage"]

    emo_sorted = emo.sort_values(by='Percentage', ascending=False)
    emo_sorted = emo[emo['Percentage'] > 1]

    sentiment_score = emo.loc[emo['Percentage'].idxmax()]['Percentage']
    sentiment_label = emo.loc[emo['Percentage'].idxmax()]['Emotion']

    emotions = dict(zip(emo_sorted['Emotion'], emo_sorted['Percentage']))

    return jsonify({
        "Predicted_Sentiment": sentiment_label,
        "cd": sentiment_score,
        "emotions": emotions
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)