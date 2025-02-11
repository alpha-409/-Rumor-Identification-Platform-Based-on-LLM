from flask import Flask, render_template, jsonify
from weibo_crawler import fetch_weibo_hot_topics, save_to_csv
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fetch-hot-topics')
def get_hot_topics():
    topics = fetch_weibo_hot_topics()
    if topics:
        # Save to CSV
        filepath = save_to_csv(topics)
        return jsonify({
            'status': 'success',
            'data': topics,
            'saved_to': filepath
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch hot topics'
        }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    app.run(debug=True)
