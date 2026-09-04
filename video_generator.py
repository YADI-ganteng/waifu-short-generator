"""
🎮 Video Generator - Larva Assets
Menggunakan gambar dari hasil extract
"""

import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

try:
    from moviepy import AudioFileClip, ImageSequenceClip
except:
    from moviepy.editor import AudioFileClip, ImageSequenceClip

class LarvaVideoGenerator:
    def __init__(self, assets_folder="larva_assets", width=1080, height=1920):
        self.assets_folder = assets_folder
        self.width = width
        self.height = height
        self.load_images()
    
    def load_images(self):
        """Load semua gambar"""
        self.images = []
        
        if os.path.exists(self.assets_folder):
            for root, dirs, files in os.walk(self.assets_folder):
                for file in files:
                    if file.endswith(('.png', '.jpg', '.jpeg')):
                        self.images.append(os.path.join(root, file))
        
        print(f"✅ {len(self.images)} images loaded")
    
    def create_background(self, frame_num=0):
        """Background"""
        img = Image.new("RGB", (self.width, self.height), (20, 20, 40))
        draw = ImageDraw.Draw(img)
        
        for y in range(self.height):
            factor = y / self.height
            r = int(20 * (1 - factor * 0.5))
            g = int(20 * (1 - factor * 0.5))
            b = int(40 * (1 - factor * 0.5))
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return img
    
    def add_sprite(self, background, frame_num=0):
        """Tambah sprite animasi"""
        if not self.images:
            return background
        
        # Animasi loop - ganti gambar setiap 3 frame
        idx = (frame_num // 3) % len(self.images)
        sprite_path = self.images[idx]
        
        try:
            sprite = Image.open(sprite_path)
            sprite = sprite.convert("RGBA")
            
            # Resize
            max_width = int(self.width * 0.7)
            max_height = int(self.height * 0.5)
            ratio = min(max_width / sprite.width, max_height / sprite.height)
            new_w = int(sprite.width * ratio)
            new_h = int(sprite.height * ratio)
            sprite = sprite.resize((new_w, new_h), Image.LANCZOS)
            
            # Posisi tengah bawah
            x = (self.width - new_w) // 2
            y = self.height - new_h - 200
            
            background.paste(sprite, (x, y), sprite)
        except:
            pass
        
        return background
    
    def add_watermark(self, image):
        """Watermark"""
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        draw.rounded_rectangle([30, self.height-120, self.width-30, self.height-20], radius=20, fill=(0,0,0,150))
        text = "YT: CeritaMistery | Penulis: Yad | Editor: Yad"
        bbox = draw.textbbox((0,0), text, font=font)
        x = (self.width - (bbox[2]-bbox[0])) // 2
        draw.text((x+2, self.height-95), text, fill="black", font=font)
        draw.text((x, self.height-97), text, fill=(255,255,255,200), font=font)
        return image
    
    def generate_video(self, duration=10):
        """Generate video"""
        fps = 30
        total_frames = int(duration * fps)
        
        print(f"🎨 {total_frames} frames...")
        
        frames = []
        for frame_num in range(total_frames):
            bg = self.create_background(frame_num)
            bg = self.add_sprite(bg, frame_num)
            bg = self.add_watermark(bg)
            frames.append(np.array(bg))
            
            if frame_num % 100 == 0:
                print(f"  Frame {frame_num}/{total_frames}")
        
        print("📹 Creating video...")
        video = ImageSequenceClip(frames, fps=fps)
        
        os.makedirs("output", exist_ok=True)
        output = "output/larva_video.mp4"
        video.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac", bitrate="2500k")
        
        video.close()
        return output

if __name__ == "__main__":
    generator = LarvaVideoGenerator()
    result = generator.generate_video(duration=10)
    print(f"\n✅ Video: {result}")
