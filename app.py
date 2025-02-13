from flask import Flask, render_template, jsonify, request, Response
import requests
from weibo_scraper import WeiboScraper
import pandas as pd
from datetime import datetime
import os
from apscheduler.schedulers.background import BackgroundScheduler

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
