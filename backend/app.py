from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path
from io import BytesIO
import docx
import PyPDF2
from werkzeug.datastructures import FileStorage



MODEL_NAME = "sangkm/go-emotions-fine-tuned-distilroberta"

def load_model():
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        return tokenizer, model

tokenizer, model = load_model()

def extract_text_from_file(file: FileStorage) -> str:
    content = file.read()
    ext = Path(file.filename).suffix.lower()
    if ext == ".txt":
        return content.decode("utf-8", errors="ignore")
    if ext == ".docx":
        doc = docx.Document(BytesIO(content))
        return "\n".join(para.text for para in doc.paragraphs)
    if ext == ".pdf":
        text_chunks = []
        reader = PyPDF2.PdfReader(BytesIO(content))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
        return "\n".join(text_chunks)
    return "Unsupported file format"



app = Flask(__name__)
CORS(app)

@app.route('/api/analyze_sms', methods=['POST'])
def analyze_sms():
    data = request.get_json()
    text = data.get('text', '')

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
    emo_sorted = emo_sorted[emo_sorted['Percentage'] > 1]
    # print(emo_sorted)

    sentiment_score = emo.loc[emo['Percentage'].idxmax()]['Percentage']
    sentiment_label = emo.loc[emo['Percentage'].idxmax()]['Emotion']

    emotions = [
        {"emotion": row.Emotion, "prob": row.Percentage}
        for _, row in emo_sorted.iterrows()
    ]
    # emotions = dict(zip(emo_sorted['Emotion'], emo_sorted['Percentage']))
    # print(emotions)

    return jsonify({
        "Predicted_Sentiment": sentiment_label,
        "cd": sentiment_score,
        "emotions": emotions
    })

@app.route('/api/analyze_document', methods=['POST'])
def analyze_document():
    file = request.files['file']
    # raw = file.read()
    # encoding = chardet.detect(raw)['encoding']
    # text = raw.decode(encoding)

    text = file.read().decode('utf-8')

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
    emo_sorted = emo_sorted[emo_sorted['Percentage'] > 1]

    sentiment_score = emo.loc[emo['Percentage'].idxmax()]['Percentage']
    sentiment_label = emo.loc[emo['Percentage'].idxmax()]['Emotion']

    # emotions = dict(zip(emo_sorted['Emotion'], emo_sorted['Percentage']))
    emotions = [
        {"emotion": row.Emotion, "prob": row.Percentage}
        for _, row in emo_sorted.iterrows()
    ]

    return jsonify({
        "Predicted_Sentiment": sentiment_label,
        "cd": sentiment_score,
        "emotions": emotions
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)