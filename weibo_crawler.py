import requests
import pandas as pd
from datetime import datetime
import json
import os

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
        'Cookie': 'UOR=www.google.com.hk,open.weibo.com,www.google.com.hk; SINAGLOBAL=4257564672237.1353.1739195402823; SCF=An1ZfR5bEm-KND6O8HIbhQHhvGPsWSGdRH0Da32DLfRCeGDoaq677XHvGA33YgntoFAiEKY_kZHGFgbNL7qZirE.; SUB=_2A25KrnTUDeRhGeFG4lIQ8i_EyjmIHXVpwogcrDV8PUNbmtB-LVT8kW9NeJJdfJDGjL4lXWwEnohMmhP0dwScigXe; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhDzVQn-cwehKWnLyNBc9Cf5JpX5KzhUgL.FoMR1K5peo2ReK-2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1h.7eKzp1h2f; ALF=02_1741787524; ULV=1739205285021:2:2:2:8476636091366.21.1739205284993:1739195402827; XSRF-TOKEN=Ww4jt0bts6AlGUo2Ir9HHI7s; WBPSESS=yuMqjfTszTqTxUEdr_jRxf9DKAQZR1K1ebi39GQiYSfo-b8vS7-AIG2oR26U_PW_p1Ue5lM2VUE3imutmdWHYKoj8xVhKjgu5wF0isrOOG5zb_Xmx4fjZR_i5j-dCBisN0Gp4ZmIOxouKsQo7ajR_A=='
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        data = response.json()
        
        # Extract relevant information from the response
        statuses = data.get('statuses', [])
        
        # Prepare data for CSV
        processed_data = []
        for status in statuses:
            processed_data.append({
                'id': status.get('id'),
                'text': status.get('text_raw', ''),
                'created_at': status.get('created_at', ''),
                'reposts_count': status.get('reposts_count', 0),
                'comments_count': status.get('comments_count', 0),
                'attitudes_count': status.get('attitudes_count', 0),
                'source': status.get('source', '')
            })
        
        return processed_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None

def save_to_csv(data, filename=None):
    if not data:
        print("No data to save")
        return
    
    if filename is None:
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'weibo_hot_topics_{timestamp}.csv'
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"Data saved to {filepath}")
    return filepath

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
