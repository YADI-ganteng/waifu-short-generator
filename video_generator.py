"""
🎬 Video Generator - Rain Effect + Transitions
Tanpa teks, hanya watermark
Fix black screen dengan gradient background
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

class RainEffect:
    """Efek hujan frame by frame"""
    
    def __init__(self, width=360, height=640):
        self.width = width
        self.height = height
        self.raindrops = []
        self.init_raindrops()
    
    def init_raindrops(self, num=80):
        """Inisialisasi raindrops"""
        self.raindrops = []
        for _ in range(num):
            self.raindrops.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'length': random.randint(8, 25),
                'speed': random.randint(8, 20),
                'opacity': random.randint(60, 160)
            })
    
    def apply(self, image, frame_num=0):
        """Apply efek hujan"""
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Update dan gambar raindrops
        for drop in self.raindrops:
            # Update posisi
            drop['y'] = (drop['y'] + drop['speed']) % self.height
            
            x = drop['x']
            y = drop['y']
            length = drop['length']
            opacity = drop['opacity']
            
            # Garis hujan
            draw.line(
                [(x, y), (x - 2, y + length)],
                fill=(180, 200, 255, opacity),
                width=1
            )
            
            # Kepala hujan
            draw.ellipse(
                [x - 1, y - 2, x + 1, y + 2],
                fill=(200, 220, 255, opacity)
            )
        
        # Composite
        image = Image.alpha_composite(image, overlay)
        return image.convert("RGB")
    
    def apply_fog(self, image, frame_num=0):
        """Efek kabut"""
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Kabut bergerak
        fog_offset = (frame_num * 2) % self.height
        
        for y in range(0, self.height, 15):
            alpha = int(25 * (1 - (y + fog_offset) % self.height / self.height))
            draw.rectangle([(0, y), (self.width, y + 15)], fill=(200, 200, 220, alpha))
        
        image = Image.alpha_composite(image, overlay)
        return image.convert("RGB")
    
    def apply_lightning(self, image, frame_num=0):
        """Efek kilat sesekali"""
        if frame_num % 120 == 0:  # Kilat setiap 5 detik (24fps * 5)
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            
            overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Flash
            draw.rectangle([(0, 0), (self.width, self.height)], fill=(255, 255, 255, 80))
            
            image = Image.alpha_composite(image, overlay)
            return image.convert("RGB")
        
        return image

class VideoGenerator:
    """Video generator lengkap"""
    
    def __init__(self, output_dir="output", video_quality="360p", part_duration=90, watermark_text="YT: CeritaMistery | Penulis: Yad | Editor: Yad"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.video_quality = video_quality
        self.part_duration = part_duration
        self.watermark_text = watermark_text
        self.resolutions = {"360p": (360, 640), "480p": (480, 854)}
        self.width, self.height = self.resolutions.get(video_quality, (360, 640))
        self.rain = RainEffect(self.width, self.height)
        
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        self.github_username = "YADI-ganteng"
        self.github_repo = "waifu-short-generator"
        
        print(f"✅ Generator: {video_quality}, Rain Effect")
    
    def create_gradient_background(self, seed=0):
        """Buat gradient background yang indah"""
        random.seed(seed)
        
        # Warna dasar gelap
        base_colors = [
            (15, 15, 35),   # Dark blue
            (25, 10, 30),   # Dark purple
            (10, 25, 25),   # Dark teal
            (30, 15, 15),   # Dark red
            (20, 20, 30),   # Dark gray
        ]
        
        base = random.choice(base_colors)
        
        # Buat gradient
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        for y in range(self.height):
            factor = y / self.height
            r = int(base[0] * (1 - factor * 0.4))
            g = int(base[1] * (1 - factor * 0.4))
            b = int(base[2] * (1 - factor * 0.4))
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # Tambah dekorasi
        for _ in range(15):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height - 150)
            radius = random.randint(15, 60)
            color = (base[0] + 20, base[1] + 20, base[2] + 30)
            draw.ellipse([x, y, x + radius, y + radius], fill=color)
        
        # Tambah bulan/lingkaran
        moon_x = random.randint(50, self.width - 50)
        moon_y = random.randint(50, 150)
        draw.ellipse([moon_x, moon_y, moon_x + 40, moon_y + 40], fill=(220, 220, 240))
        draw.ellipse([moon_x + 10, moon_y - 5, moon_x + 35, moon_y + 20], fill=base)
        
        return img
    
    def try_download_image(self, scene_text):
        """Coba download gambar, fallback ke gradient"""
        try:
            # Coba Picsum
            url = f"https://picsum.photos/{self.width}/{self.height}?random={random.randint(1, 1000)}"
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200 and len(response.content) > 1000:
                img = Image.open(BytesIO(response.content))
                img = img.convert("RGB")
                img = img.resize((self.width, self.height), Image.LANCZOS)
                return img
        except:
            pass
        
        # Fallback ke gradient
        seed = len(scene_text) + random.randint(0, 100)
        return self.create_gradient_background(seed)
    
    def add_watermark(self, image):
        """Tambahkan watermark kecil"""
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        # Watermark background
        draw.rounded_rectangle(
            [10, self.height - 55, self.width - 10, self.height - 10],
            radius=10,
            fill=(0, 0, 0, 100)
        )
        
        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image)
        
        # Text watermark
        lines = self.watermark_text.split("|")
        y = self.height - 48
        
        for line in lines:
            line = line.strip()
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (self.width - (bbox[2] - bbox[0])) // 2
            draw.text((x + 1, y + 1), line, fill="black", font=font)
            draw.text((x, y), line, fill=(255, 255, 255, 180), font=font)
            y += 16
        
        return image.convert("RGB")
    
    def split_script(self, script, max_duration=90):
        """Split script menjadi parts"""
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
        """Buat satu part video"""
        print(f"\n{'='*50}")
        print(f"🎬 Part {part_num}")
        print(f"{'='*50}")
        
        # TTS
        print("🔊 Audio...")
        tts = gTTS(text=script, lang="id", slow=False)
        audio_file = f"{self.output_dir}/temp_{part_num}.mp3"
        tts.save(audio_file)
        
        audio_clip = AudioFileClip(audio_file)
        duration = audio_clip.duration
        print(f"⏱️ {duration:.1f}s")
        
        # Scenes
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        num_scenes = min(max(len(sentences), 3), 5)
        
        # Generate scene images
        print("📸 Generating scene images...")
        scene_images = []
        for i in range(num_scenes):
            scene_text = sentences[i] if i < len(sentences) else script
            img = self.try_download_image(scene_text)
            scene_images.append(img)
            print(f"  Scene {i+1} ready")
        
        # Generate frames
        fps = 24
        total_frames = int(duration * fps)
        frames_per_scene = total_frames // num_scenes
        
        print(f"🎨 Generating {total_frames} frames dengan efek...")
        
        video_frames = []
        for frame_num in range(total_frames):
            # Pilih scene
            scene_idx = min(frame_num // frames_per_scene, num_scenes - 1)
            
            # Transisi antar scene
            frame_in_scene = frame_num % frames_per_scene
            if frame_in_scene < 10 and scene_idx > 0:
                # Crossfade
                progress = frame_in_scene / 10
                img1 = np.array(scene_images[scene_idx - 1]).astype(float)
                img2 = np.array(scene_images[scene_idx]).astype(float)
                blended = img1 * (1 - progress) + img2 * progress
                img = Image.fromarray(blended.astype(np.uint8))
            else:
                img = scene_images[scene_idx]
            
            # Apply efek hujan
            img = self.rain.apply(img, frame_num)
            
            # Apply fog (subtle)
            if frame_num % 3 == 0:
                img = self.rain.apply_fog(img, frame_num)
            
            # Apply lightning (occasional)
            img = self.rain.apply_lightning(img, frame_num)
            
            # Add watermark
            img = self.add_watermark(img)
            
            video_frames.append(np.array(img))
            
            if frame_num % 50 == 0:
                print(f"  Frame {frame_num}/{total_frames}")
        
        # Buat video
        print("📹 Creating video...")
        video = ImageSequenceClip(video_frames, fps=fps)
        
        if MOVIEPY_V2:
            video = video.with_audio(audio_clip)
        else:
            video = video.set_audio(audio_clip)
        
        output_path = f"{self.output_dir}/part_{part_num}.mp4"
        print("💾 Exporting...")
        video.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            bitrate="800k",
            preset="ultrafast"
        )
        
        video.close()
        audio_clip.close()
        
        print(f"✅ Part {part_num} done!")
        return output_path
    
    def generate_all(self, script):
        """Generate semua parts"""
        parts = self.split_script(script, self.part_duration)
        print(f"\n📝 {len(parts)} parts")
        
        results = []
        for i, part in enumerate(parts):
            video_path = self.create_part(part, i + 1)
            results.append(video_path)
        
        return results

if __name__ == "__main__":
    generator = VideoGenerator(
        video_quality="360p",
        part_duration=90,
        watermark_text="YT: CeritaMistery | Penulis: Yad | Editor: Yad"
    )
    
    # Load stories
    stories_dir = "stories"
    if os.path.exists(stories_dir):
        txt_files = [f for f in os.listdir(stories_dir) if f.endswith('.txt')]
        for txt_file in txt_files:
            with open(os.path.join(stories_dir, txt_file), "r") as f:
                script = f.read()
            results = generator.generate_all(script)
            print(f"\n✅ {len(results)} parts!")
    else:
        script = "Di sebuah desa terpencil, terjadi kejadian aneh. Setiap malam terdengar suara misterius dari hutan."
        results = generator.generate_all(script)
        print(f"\n✅ {len(results)} parts!")
