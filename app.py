
from flask import Flask, render_template, request, jsonify, send_from_directory
import os, datetime, csv

app = Flask(__name__)
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)
LOG_CSV = os.path.join(LOG_DIR, 'analysis.csv')
if not os.path.exists(LOG_CSV):
    with open(LOG_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp','brightness','audio_level','wpm','emotion','sentiment','state','recommendation'])

def decide_state(brightness, audio_level, wpm, emotion, sentiment):
    score = 0
    if brightness > 110: score += 1
    if audio_level < 0.02: score += 1
    if wpm > 20: score += 1
    if emotion == 'happy': score += 1
    if sentiment == 'positive': score += 1

    if score >= 3:
        return 'focused', 'Focused — Continue. Take a short break later.'
    elif score == 2:
        return 'neutral', 'Mixed signals — try 2-min breathing or upbeat music.'
    else:
        return 'distracted_or_tired', 'Tired/distracted — take 5-min walk or listen to calming music.'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    brightness = data.get('brightness', 0)
    audio_level = data.get('audio_level', 0.0)
    wpm = data.get('wpm', 0.0)
    emotion = data.get('emotion', 'neutral')
    sentiment = data.get('sentiment', 'neutral')

    state, recommendation = decide_state(brightness, audio_level, wpm, emotion, sentiment)

    with open(LOG_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.utcnow().isoformat()+'Z', brightness, audio_level, wpm, emotion, sentiment, state, recommendation])

    return jsonify({'state': state, 'recommendation': recommendation, 'received': data})

@app.route('/logs/<path:filename>')
def download_log(filename):
    return send_from_directory('logs', filename, as_attachment=True)

import os
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)   
