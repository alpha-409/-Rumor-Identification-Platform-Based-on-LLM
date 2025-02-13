import requests
import pandas as pd
from datetime import datetime
import json
import os

class WeiboScraper:
    def __init__(self):
        self.base_url = "https://weibo.com/ajax/feed/hottimeline"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://weibo.com/",
            "Cookie": "UOR=www.google.com.hk,open.weibo.com,www.google.com.hk; SINAGLOBAL=4257564672237.1353.1739195402823; SCF=An1ZfR5bEm-KND6O8HIbhQHhvGPsWSGdRH0Da32DLfRCeGDoaq677XHvGA33YgntoFAiEKY_kZHGFgbNL7qZirE.; XSRF-TOKEN=Ww4jt0bts6AlGUo2Ir9HHI7s; _s_tentry=weibo.com; Apache=9424135483965.553.1739429271046; ULV=1739429271050:3:3:3:9424135483965.553.1739429271046:1739205285021; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhDzVQn-cwehKWnLyNBc9Cf5JpVF024SKn7S0nRSh-E; SUB=_2AkMQ8S5BdcPxrARZkfgUzmrqbYhH-jyjJEe3An7uJhMyAxhq7m8FqSVutBF-XKdj8v-OLu6kcyYfnHPftTXjbgO0; WBPSESS=Dt2hbAUaXfkVprjyrAZT_Lb8hpbrsD4tvepY6wxH0Foflauh7jiB5njTgYGrEfm6Iq51SbPSpPAACh6r5LOs4tZTrVE2pRZCuTQf4j4Nli5ZyjEIk0NRK8cOyoZjgktOVYlmgKc3w2-wClRX6PhwhQ=="
        }

    def fetch_hot_timeline(self):
        params = {
            "since_id": "0",
            "refresh": "0",
            "group_id": "102803",
            "containerid": "102803",
            "extparam": "discover|new_feed",
            "max_id": "0",
            "count": "30"
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            print("Raw API Response:", json.dumps(data, ensure_ascii=False)[:1000])
            if 'data' in data:
                return data['data']
            return data
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def process_data(self, data):
        if not data:
            print("No data received from API")
            return pd.DataFrame()
            
        # Check for different possible data structures
        statuses = None
        if 'statuses' in data:
            statuses = data['statuses']
            print("Found statuses directly in data")
        elif 'data' in data and 'statuses' in data['data']:
            statuses = data['data']['statuses']
            print("Found statuses in data['data']")
        elif isinstance(data, list):
            statuses = data
            print("Data is a list of statuses")
            
        if not statuses:
            print("No statuses found in data")
            return pd.DataFrame()

        print(f"Processing {len(statuses)} statuses")
        processed_data = []
        for idx, status in enumerate(statuses):
            try:
                # Handle both text and text_raw fields
                text = status.get('text_raw', status.get('text', ''))
                
                user = status.get('user', {})
                print(f"\nProcessing status {idx + 1}:")
                print("User data:", json.dumps(user, ensure_ascii=False))
                
                # Try to get the HD avatar first, then fallback to other options
                avatar_url = None
                if user:
                    avatar_url = (
                        user.get('avatar_hd') or
                        user.get('avatar_large') or
                        user.get('profile_image_url')
                    )
                    print(f"Found avatar URL: {avatar_url}")
                
                if not avatar_url:
                    avatar_url = 'https://tvax3.sinaimg.cn/default/images/default_avatar_male_50.gif'
                    print("Using default avatar")
                
                processed_status = {
                    'created_at': status.get('created_at', ''),
                    'text': text,
                    'user_name': user.get('screen_name', ''),
                    'user_avatar': avatar_url,
                    'reposts_count': status.get('reposts_count', 0),
                    'comments_count': status.get('comments_count', 0),
                    'attitudes_count': status.get('attitudes_count', 0)
                }
                processed_data.append(processed_status)
            except Exception as e:
                print(f"Error processing status: {e}")
                continue

        df = pd.DataFrame(processed_data)
        print("\nProcessed DataFrame columns:", df.columns.tolist())
        print("DataFrame shape:", df.shape)
        return df

    def save_to_csv(self, df):
        if df.empty:
            return None
            
        filename = 'weibo_data.csv'
        try:
            # Convert Weibo date format to datetime and localize to UTC
            df['created_at'] = pd.to_datetime(df['created_at'], format='%a %b %d %H:%M:%S +0800 %Y').dt.tz_localize(None)
            
            # Try to read existing data
            if os.path.exists(filename):
                existing_df = pd.read_csv(filename)
                existing_df['created_at'] = pd.to_datetime(existing_df['created_at']).dt.tz_localize(None)
                # Remove duplicates based on created_at and text
                df = pd.concat([existing_df, df]).drop_duplicates(subset=['created_at', 'text'], keep='last')
                # Sort by created_at in descending order
                df = df.sort_values('created_at', ascending=False)
                # Keep only the most recent 1000 posts
                df = df.head(1000)
            
            # Convert datetime back to string for storage
            df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
            # Save the combined data
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            return filename
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return None

    def run(self):
        try:
            print("Fetching data from Weibo API...")
            data = self.fetch_hot_timeline()
            if not data:
                print("No data received from fetch_hot_timeline")
                return None
                
            print("\nProcessing data...")
            df = self.process_data(data)
            if df.empty:
                print("No data after processing")
                return None
                
            print(f"\nProcessed {len(df)} items")
            filename = self.save_to_csv(df)
            if filename:
                print(f"Data saved to {filename}")
                return filename
            print("Failed to save data to file")
            return None
        except Exception as e:
            print(f"Error in run: {str(e)}")
            return None

if __name__ == "__main__":
    scraper = WeiboScraper()
    filename = scraper.run()
    if filename:
        print(f"Data saved to {filename}")
        # Print the first few rows to verify the data
        df = pd.read_csv(filename)
        print("\nFirst few rows of saved data:")
        print(df[['user_name', 'user_avatar']].head())
    else:
        print("Failed to fetch or save data")
