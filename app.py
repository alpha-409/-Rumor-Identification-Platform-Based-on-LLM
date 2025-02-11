from flask import Flask, render_template, jsonify, request, Response
from weibo_crawler import fetch_weibo_hot_topics, save_to_csv
from flask_cors import CORS
import requests
import os
import time
import hashlib
import glob

app = Flask(__name__)
CORS(app)

# 图片缓存配置
CACHE_DIR = 'cache/images'
CACHE_TIMEOUT = 3600  # 1小时缓存过期
MAX_CACHE_SIZE = 500 * 1024 * 1024  # 500MB 最大缓存大小

def get_cache_filename(url):
    """生成缓存文件名"""
    # 使用URL的MD5作为文件名
    hash_object = hashlib.md5(url.encode())
    filename = hash_object.hexdigest()
    # 保留原始扩展名
    ext = os.path.splitext(url)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        filename += ext
    else:
        filename += '.jpg'  # 默认使用.jpg
    return os.path.join(CACHE_DIR, filename)

def clean_old_cache():
    """清理过期和超量的缓存文件"""
    try:
        if not os.path.exists(CACHE_DIR):
            return

        # 获取所有缓存文件
        cache_files = glob.glob(os.path.join(CACHE_DIR, '*.*'))
        now = time.time()
        
        # 按照修改时间排序
        cache_files.sort(key=lambda x: os.path.getmtime(x))
        
        total_size = 0
        for file_path in cache_files:
            # 删除过期文件
            if now - os.path.getmtime(file_path) > CACHE_TIMEOUT:
                os.remove(file_path)
                continue
                
            # 计算总大小并在超过限制时删除最旧的文件
            total_size += os.path.getsize(file_path)
            if total_size > MAX_CACHE_SIZE:
                os.remove(file_path)
                
    except Exception as e:
        print(f"Error cleaning cache: {e}")

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

@app.route('/api/proxy-image')
def proxy_image():
    """带缓存的图片代理"""
    url = request.args.get('url')
    if not url:
        return 'Missing URL parameter', 400

    # 创建缓存目录
    os.makedirs(CACHE_DIR, exist_ok=True)

    # 生成缓存文件路径
    cache_file = get_cache_filename(url)

    try:
        # 检查缓存是否存在且未过期
        if os.path.exists(cache_file):
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < CACHE_TIMEOUT:
                with open(cache_file, 'rb') as f:
                    content = f.read()
                    content_type = 'image/jpeg'
                    if cache_file.endswith('.png'):
                        content_type = 'image/png'
                    elif cache_file.endswith('.gif'):
                        content_type = 'image/gif'
                    elif cache_file.endswith('.webp'):
                        content_type = 'image/webp'
                    return Response(content, 
                                 mimetype=content_type,
                                 headers={'Cache-Control': 'public, max-age=31536000'})

        # 如果缓存不存在或已过期，重新获取图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer': 'https://weibo.com/',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content = response.content
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # 保存到缓存
        with open(cache_file, 'wb') as f:
            f.write(content)

        # 清理旧缓存
        clean_old_cache()

        # 返回图片内容
        return Response(
            content,
            mimetype=content_type,
            headers={
                'Cache-Control': 'public, max-age=31536000'
            }
        )
    except Exception as e:
        print(f"Error proxying image {url}: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # 启动时清理旧缓存
    clean_old_cache()
    
    app.run(debug=True)
