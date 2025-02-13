from flask import Flask, render_template, jsonify, request, Response
import requests
from weibo_scraper import WeiboScraper
import pandas as pd
from datetime import datetime
import os
from apscheduler.schedulers.background import BackgroundScheduler
import jieba
from collections import Counter
import numpy as np

app = Flask(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()

# Function to read the data from CSV
def read_data():
    filename = 'weibo_data.csv'
    try:
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at', ascending=False)
            return df.to_dict('records')
        else:
            print("Data file does not exist")
    except Exception as e:
        print(f"Error reading data: {e}")
    return []

# Scrape function that is triggered every 10 seconds
def scrape_data():
    try:
        scraper = WeiboScraper()
        filename = scraper.run()
        if filename:
            print("Data scraped successfully")
            data = read_data()
            if data:
                print("Data refreshed")
                print(f"Total records after refresh: {len(data)}")
    except Exception as e:
        print(f"Error scraping data: {e}")

# Schedule the scraper to run every 10 seconds
scheduler.add_job(scrape_data, 'interval', seconds=10)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/analysis/wordcloud')
def get_wordcloud_data():
    try:
        df = pd.read_csv('weibo_data.csv')
        # 合并所有文本
        text = ' '.join(df['text'].astype(str))
        # 使用结巴分词
        words = jieba.cut(text)
        # 过滤停用词和特殊字符
        stop_words = {'的', '了', '在', '是', '我', '你', '他', '她', '它', '这', '那', '和', '与', '就', '都', '而', '且', '但', '转发', '微博', '啊', '吧', '呢', '哦', '哈', ' '}
        words = [word for word in words if len(word) > 1 and word not in stop_words]
        # 统计词频
        word_freq = Counter(words).most_common(100)
        # 构造词云数据
        word_cloud_data = [{"name": word, "value": count} for word, count in word_freq]
        return jsonify({"success": True, "data": word_cloud_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/analysis/time_distribution')
def get_time_distribution():
    try:
        df = pd.read_csv('weibo_data.csv')
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['hour'] = df['created_at'].dt.hour
        df['weekday'] = df['created_at'].dt.weekday
        
        # 创建7x24的时间分布矩阵
        time_matrix = np.zeros((7, 24))
        for _, row in df.iterrows():
            time_matrix[row['weekday']][row['hour']] += 1
        
        # 构造热力图数据
        heatmap_data = []
        for week in range(7):
            for hour in range(24):
                heatmap_data.append([hour, week, int(time_matrix[week][hour])])
        
        return jsonify({
            "success": True,
            "data": heatmap_data
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/analysis/hourly_trend')
def get_hourly_trend():
    try:
        df = pd.read_csv('weibo_data.csv')
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['hour'] = df['created_at'].dt.hour
        
        # 统计每小时的帖子数
        hourly_counts = df['hour'].value_counts().sort_index()
        
        return jsonify({
            "success": True,
            "data": {
                "hours": list(range(24)),
                "counts": [int(hourly_counts.get(hour, 0)) for hour in range(24)]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/refresh')
def refresh_data():
    try:
        scraper = WeiboScraper()
        filename = scraper.run()
        if filename:
            data = read_data()
            if data:
                return jsonify({
                    "success": True,
                    "message": "Data refreshed successfully",
                    "data": data
                })
        print("No data returned from scraper")
        return jsonify({
            "success": False,
            "message": "No data available from Weibo"
        })
    except Exception as e:
        print(f"Error refreshing data: {e}")
        return jsonify({
            "success": False,
            "message": f"Error refreshing data: {str(e)}"
        })

@app.route('/data')
def get_data():
    try:
        page = int(request.args.get('page', 1))
        per_page = 10
        
        data = read_data()
        if not data:
            print("No existing data found, fetching new data...")
            scraper = WeiboScraper()
            filename = scraper.run()
            if filename:
                data = read_data()
        
        if data:
            # Calculate pagination
            total_items = len(data)
            total_pages = (total_items + per_page - 1) // per_page
            
            # Get slice of data for current page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_data = data[start_idx:end_idx]
            
            return jsonify({
                "success": True,
                "data": page_data,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "per_page": per_page
                },
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return jsonify({
            "success": False,
            "message": "Unable to fetch Weibo data"
        })
    except Exception as e:
        print(f"Error getting data: {e}")
        return jsonify({
            "success": False,
            "message": f"Error getting data: {str(e)}"
        })

@app.route('/proxy/image')
def proxy_image():
    image_url = request.args.get('url')
    if not image_url or image_url == 'undefined':
        return Response('Invalid URL', status=400)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": "https://weibo.com/",
            "Cookie": "UOR=www.google.com.hk,open.weibo.com,www.google.com.hk; SINAGLOBAL=4257564672237.1353.1739195402823"
        }
        response = requests.get(image_url, headers=headers, stream=True)
        response.raise_for_status()
        return Response(
            response.content,
            content_type=response.headers['content-type'],
            status=response.status_code
        )
    except Exception as e:
        print(f"Error proxying image: {e}")
        return Response('Error fetching image', status=500)

if __name__ == '__main__':
    # Enable more detailed error logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Start the scheduler
    scheduler.start()

    app.run(debug=True)
