import requests
import pandas as pd
from datetime import datetime
import json
import os
import re

def get_weibo_image_url(pic_info):
    """从pic_info中获取最佳图片URL"""
    try:
        # 按优先级获取图片URL
        if 'large' in pic_info:
            url = pic_info['large'].get('url', '')
        elif 'original' in pic_info:
            url = pic_info['original'].get('url', '')
        elif 'middleplus' in pic_info:
            url = pic_info['middleplus'].get('url', '')
        else:
            return ''

        # 确保URL使用HTTPS
        if url.startswith('//'):
            url = 'https:' + url
        return url
    except Exception:
        return ''

def get_weibo_avatar_url(user):
    """获取用户头像URL"""
    try:
        # 按优先级获取头像URL
        avatar_url = (user.get('avatar_hd', '') or 
                     user.get('avatar_large', '') or 
                     user.get('profile_image_url', ''))
        
        if avatar_url:
            if avatar_url.startswith('//'):
                avatar_url = 'https:' + avatar_url
            # 移除URL参数
            avatar_url = avatar_url.split('?')[0]
            return avatar_url
        return ''
    except Exception:
        return ''

def fetch_weibo_hot_topics():
    url = "https://weibo.com/ajax/feed/hottimeline"
    
    params = {
        "since_id": "0",
        "refresh": "0",
        "group_id": "102803",
        "containerid": "102803",
        "extparam": "discover|new_feed",
        "max_id": "0",
        "count": "10"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Cookie': 'UOR=www.google.com.hk,open.weibo.com,www.google.com.hk; SINAGLOBAL=4257564672237.1353.1739195402823; SCF=An1ZfR5bEm-KND6O8HIbhQHhvGPsWSGdRH0Da32DLfRCeGDoaq677XHvGA33YgntoFAiEKY_kZHGFgbNL7qZirE.; SUB=_2A25KrnTUDeRhGeFG4lIQ8i_EyjmIHXVpwogcrDV8PUNbmtB-LVT8kW9NeJJdfJDGjL4lXWwEnohMmhP0dwScigXe; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhDzVQn-cwehKWnLyNBc9Cf5JpX5KzhUgL.FoMR1K5peo2ReK-2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1h.7eKzp1h2f; ALF=02_1741787524; ULV=1739205285021:2:2:2:8476636091366.21.1739205284993:1739195402827; XSRF-TOKEN=Ww4jt0bts6AlGUo2Ir9HHI7s; WBPSESS=yuMqjfTszTqTxUEdr_jRxf9DKAQZR1K1ebi39GQiYSfo-b8vS7-AIG2oR26U_PW_p1Ue5lM2VUE3imutmdWHYKoj8xVhKjgu5wF0isrOOG5zb_Xmx4fjZR_i5j-dCBisN0Gp4ZmIOxouKsQo7ajR_A==',
        'Referer': 'https://weibo.com/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        statuses = data.get('statuses', [])
        
        processed_data = []
        for status in statuses:
            user = status.get('user', {})
            
            # 获取图片URLs
            pic_urls = []
            pic_infos = status.get('pic_infos', {})
            for pic_id, pic_info in pic_infos.items():
                pic_url = get_weibo_image_url(pic_info)
                if pic_url:
                    pic_urls.append(pic_url)
            
            # 获取用户头像
            avatar_url = get_weibo_avatar_url(user)
            
            processed_data.append({
                'id': status.get('id'),
                'text': status.get('text_raw', ''),
                'created_at': datetime.strptime(status.get('created_at', ''), '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d %H:%M:%S'),
                'reposts_count': status.get('reposts_count', 0),
                'comments_count': status.get('comments_count', 0),
                'attitudes_count': status.get('attitudes_count', 0),
                'source': status.get('source', ''),
                'user_id': user.get('id', ''),
                'user_name': user.get('screen_name', ''),
                'user_avatar': avatar_url,
                'user_followers_count': user.get('followers_count', 0),
                'user_friends_count': user.get('friends_count', 0),
                'images': '|'.join(pic_urls) if pic_urls else ''
            })
        
        return processed_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def save_to_csv(data, filepath='data/weibo_hot_topics.csv'):
    if not data:
        print("No data to save")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Convert new data to DataFrame
    new_df = pd.DataFrame(data)
    
    try:
        # Try to read existing CSV file
        if os.path.exists(filepath):
            existing_df = pd.read_csv(filepath)
            # Combine existing and new data
            combined_df = pd.concat([existing_df, new_df])
            # Drop duplicates based on id
            combined_df.drop_duplicates(subset=['id'], keep='last', inplace=True)
        else:
            combined_df = new_df
        
        # Sort by created_at in descending order
        combined_df.sort_values('created_at', ascending=False, inplace=True)
        
        # Save to CSV
        combined_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"Data saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving data: {e}")
        return None

def main():
    # Fetch data from Weibo
    print("Fetching hot topics from Weibo...")
    hot_topics = fetch_weibo_hot_topics()
    
    if hot_topics:
        # Save to CSV
        saved_file = save_to_csv(hot_topics)
        print(f"Successfully saved {len(hot_topics)} topics to {saved_file}")
    else:
        print("Failed to fetch data from Weibo")

if __name__ == "__main__":
    main()
