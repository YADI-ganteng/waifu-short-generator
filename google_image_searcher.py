"""
🖼️ Google Image Searcher
"""

import requests
import os
import hashlib
from PIL import Image
from io import BytesIO

class GoogleImageSearcher:
    def __init__(self, save_dir="images"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        self.headers = {"User-Agent": "Mozilla/5.0"}
    
    def search_images(self, query, num_images=5):
        print(f"Searching: {query}")
        image_urls = []
        
        try:
            keywords = query.replace(' ', '-')
            for i in range(num_images):
                url = f"https://source.unsplash.com/800x1200/?{keywords},{i}"
                image_urls.append(url)
        except:
            pass
        
        if len(image_urls) < num_images:
            for i in range(num_images - len(image_urls)):
                url = f"https://picsum.photos/800/1200?random={i}"
                image_urls.append(url)
        
        return image_urls[:num_images]
    
    def download_image(self, url, filename=None):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                if not filename:
                    hash_name = hashlib.md5(url.encode()).hexdigest()[:10]
                    filename = f"{hash_name}.jpg"
                filepath = os.path.join(self.save_dir, filename)
                img.save(filepath)
                return filepath
            return None
        except:
            return None
    
    def get_images_for_scene(self, scene_text, character_prompt, style, num_images=3):
        keywords = self.extract_keywords(scene_text)
        query = f"{keywords} {style} {character_prompt}"
        image_urls = self.search_images(query, num_images)
        
        downloaded = []
        for i, url in enumerate(image_urls):
            filepath = self.download_image(url, f"scene_{i}.jpg")
            if filepath:
                downloaded.append(filepath)
        
        return downloaded
    
    def extract_keywords(self, text, max_words=5):
        stop_words = ['yang', 'di', 'ke', 'dari', 'dan', 'atau', 'untuk', 'dengan', 'pada', 'ini', 'itu', 'adalah', 'sebuah', 'seorang']
        words = text.split()
        keywords = [w for w in words if w.lower() not in stop_words]
        return ' '.join(keywords[:max_words])
