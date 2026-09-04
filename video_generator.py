"""
🎬 YouTube Shorts Generator - 1080x1920
Rain Effect + Transitions + Watermark
Tanpa Teks Overlay
"""

import os
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from gtts import gTTS
from datetime import datetime
import requests
import random
from io import BytesIO

try:
    from moviepy import AudioFileClip, ImageSequenceClip
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import AudioFileClip, ImageSequenceClip
    MOVIEPY_V2 = False

WIDTH = 1080
HEIGHT = 1920
FPS = 30
PART_DURATION = 90

class RainEffect:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.raindrops = []
        self.init_raindrops()
    
    def init_raindrops(self, num=200):
        self.raindrops = []
        for _ in range(num):
            self.raindrops.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'length': random.randint(20, 60),
                'speed': random.randint(15, 40),
                'opacity': random.randint(50, 180),
                'thickness': random.randint(1, 3)
            })
    
    def apply(self, image, frame_num=0):
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        for drop in self.raindrops:
            drop['y'] = (drop['y'] + drop['speed']) % self.height
            x, y, length = drop['x'], drop['y'], drop['length']
            opacity, thickness = drop['opacity'], drop['thickness']
            
            draw.line([(x, y), (x - 3, y + length)], fill=(180, 200, 255, opacity), width=thickness)
            draw.ellipse([x - 2, y - 3, x + 2, y + 3], fill=(200, 220, 255, opacity))
        
        image = Image.alpha_composite(image, overlay)
        return image.convert("RGB")
    
    def apply_fog(self, image, frame_num=0):
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        fog_offset = (frame_num * 3) % self.height
        for y in range(0, self.height, 30):
            alpha = int(20 * (1 - (y + fog_offset) % self.height / self.height))
            draw.rectangle([(0, y), (self.width, y + 30)], fill=(200, 200, 220, alpha))
        
        image = Image.alpha_composite(image, overlay)
        return image.convert("RGB")
    
    def apply_lightning(self, image, frame_num=0):
        if frame_num % 90 == 0:
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            draw.rectangle([(0, 0), (self.width, self.height)], fill=(255, 255, 255, 60))
            
            bolt_x = random.randint(100, self.width - 100)
            bolt_points = [(bolt_x, 0)]
            y = 0
            while y < self.height:
                y += random.randint(50, 150)
                x = bolt_x + random.randint(-30, 30)
                bolt_points.append((x, y))
            
            draw.line(bolt_points, fill=(255, 255, 200, 150), width=3)
            
            image = Image.alpha_composite(image, overlay)
            return image.convert("RGB")
        return image

class YTShortGenerator:
    def __init__(self, output_dir="output", watermark_text="YT: CeritaMistery | Penulis: Yad | Editor: Yad"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.width = WIDTH
        self.height = HEIGHT
        self.watermark_text = watermark_text
        self.rain = RainEffect(self.width, self.height)
        print(f"✅ YT Short: {self.width}x{self.height}")
    
    def create_gradient_background(self, seed=0):
        random.seed(seed)
        base_colors = [(15, 15, 35), (25, 10, 30), (10, 25, 25), (30, 15, 15), (20, 20, 30)]
        base = random.choice(base_colors)
        
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        for y in range(self.height):
            factor = y / self.height
            r = int(base[0] * (1 - factor * 0.5))
            g = int(base[1] * (1 - factor * 0.5))
            b = int(base[2] * (1 - factor * 0.5))
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        for _ in range(30):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height - 300)
            radius = random.randint(30, 150)
            color = (base[0] + 15, base[1] + 15, base[2] + 25)
            draw.ellipse([x, y, x + radius, y + radius], fill=color)
        
        moon_x = random.randint(200, self.width - 200)
        moon_y = random.randint(100, 300)
        draw.ellipse([moon_x, moon_y, moon_x + 100, moon_y + 100], fill=(220, 220, 240))
        draw.ellipse([moon_x + 25, moon_y - 10, moon_x + 85, moon_y + 50], fill=base)
        
        return img
    
    def try_download_image(self, scene_text):
        try:
            url = f"https://picsum.photos/{self.width}/{self.height}?random={random.randint(1, 1000)}"
            response = requests.get(url, timeout=15, allow_redirects=True)
            if response.status_code == 200 and len(response.content) > 5000:
                img = Image.open(BytesIO(response.content))
                img = img.convert("RGB")
                img = img.resize((self.width, self.height), Image.LANCZOS)
                return img
        except:
            pass
        return self.create_gradient_background(len(scene_text))
    
    def add_watermark(self, image):
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        draw.rounded_rectangle([30, self.height - 120, self.width - 30, self.height - 20], radius=20, fill=(0, 0, 0, 100))
        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image)
        
        lines = self.watermark_text.split("|")
        y = self.height - 100
        for line in lines:
            line = line.strip()
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (self.width - (bbox[2] - bbox[0])) // 2
            draw.text((x + 2, y + 2), line, fill="black", font=font)
            draw.text((x, y), line, fill=(255, 255, 255, 180), font=font)
            y += 35
        
        return image.convert("RGB")
    
    def split_script(self, script, max_duration=PART_DURATION):
        words = script.split()
        if len(words) / 2.5 <= max_duration:
            return [script]
        
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        parts = []
        current_part = []
        current_words = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            if current_words + sentence_words > max_duration * 2.5:
                if current_part:
                    parts.append('. '.join(current_part) + '.')
                current_part = [sentence]
                current_words = sentence_words
            else:
                current_part.append(sentence)
                current_words += sentence_words
        
        if current_part:
            parts.append('. '.join(current_part) + '.')
        return parts
    
    def create_part(self, script, part_num):
        print(f"\n{'='*50}")
        print(f"🎬 Part {part_num}")
        print(f"{'='*50}")
        
        tts = gTTS(text=script, lang="id", slow=False)
        audio_file = f"{self.output_dir}/temp_{part_num}.mp3"
        tts.save(audio_file)
        
        audio_clip = AudioFileClip(audio_file)
        duration = audio_clip.duration
        print(f"⏱️ {duration:.1f}s")
        
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        num_scenes = min(max(len(sentences), 3), 5)
        
        print("📸 Images...")
        scene_images = []
        for i in range(num_scenes):
            scene_text = sentences[i] if i < len(sentences) else script
            img = self.try_download_image(scene_text)
            scene_images.append(img)
            print(f"  Scene {i+1} ready")
        
        fps = FPS
        total_frames = int(duration * fps)
        frames_per_scene = total_frames // num_scenes
        
        print(f"🎨 {total_frames} frames...")
        video_frames = []
        
        for frame_num in range(total_frames):
            scene_idx = min(frame_num // frames_per_scene, num_scenes - 1)
            frame_in_scene = frame_num % frames_per_scene
            
            if frame_in_scene < 15 and scene_idx > 0:
                progress = frame_in_scene / 15
                img1 = np.array(scene_images[scene_idx - 1]).astype(float)
                img2 = np.array(scene_images[scene_idx]).astype(float)
                blended = img1 * (1 - progress) + img2 * progress
                img = Image.fromarray(blended.astype(np.uint8))
            else:
                img = scene_images[scene_idx]
            
            img = self.rain.apply(img, frame_num)
            
            if frame_num % 3 == 0:
                img = self.rain.apply_fog(img, frame_num)
            
            img = self.rain.apply_lightning(img, frame_num)
            
            img = self.add_watermark(img)
            
            video_frames.append(np.array(img))
            
            if frame_num % 100 == 0:
                print(f"  Frame {frame_num}/{total_frames}")
        
        print("📹 Creating video...")
        video = ImageSequenceClip(video_frames, fps=fps)
        
        if MOVIEPY_V2:
            video = video.with_audio(audio_clip)
        else:
            video = video.set_audio(audio_clip)
        
        output_path = f"{self.output_dir}/yt_short_part_{part_num}.mp4"
        print("💾 Exporting...")
        video.write_videofile(output_path, fps=fps, codec="libx264", audio_codec="aac", bitrate="2500k", preset="medium")
        
        video.close()
        audio_clip.close()
        
        print(f"✅ Part {part_num} done!")
        return output_path
    
    def generate_all(self, script):
        parts = self.split_script(script, PART_DURATION)
        print(f"\n📝 {len(parts)} parts")
        
        results = []
        for i, part in enumerate(parts):
            video_path = self.create_part(part, i + 1)
            results.append(video_path)
        return results

if __name__ == "__main__":
    generator = YTShortGenerator(watermark_text="YT: CeritaMistery | Penulis: Yad | Editor: Yad")
    
    stories_dir = "stories"
    if os.path.exists(stories_dir):
        txt_files = [f for f in os.listdir(stories_dir) if f.endswith('.txt')]
        for txt_file in txt_files:
            with open(os.path.join(stories_dir, txt_file), "r") as f:
                script = f.read()
            results = generator.generate_all(script)
            print(f"\n✅ {len(results)} YT Shorts!")
    else:
        script = "Di sebuah desa terpencil, terjadi kejadian aneh. Setiap malam terdengar suara misterius."
        results = generator.generate_all(script)
        print(f"\n✅ {len(results)} YT Shorts!")
