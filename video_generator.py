"""
🎬 Video Generator - 360p + Auto Part + Watermark + Auto Convert
"""

import os
import json
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from gtts import gTTS
from google_image_searcher import GoogleImageSearcher

try:
    from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
    MOVIEPY_V2 = True
except ImportError:
    from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
    MOVIEPY_V2 = False

class GoogleImageVideoGenerator:
    def __init__(self, output_dir="output", video_quality="360p", part_duration=90, watermark_text="YT: CeritaMistery | Penulis: Yad | Editor: Yad"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.video_quality = video_quality
        self.part_duration = part_duration
        self.watermark_text = watermark_text
        self.resolutions = {"360p": (360, 640), "480p": (480, 854), "720p": (720, 1280)}
        self.width, self.height = self.resolutions.get(video_quality, (360, 640))
        self.searcher = GoogleImageSearcher()
        print(f"Generator: {video_quality}, {part_duration}s")
    
    def auto_convert_to_scenes(self, script_text, max_scenes=5):
        """Auto convert script menjadi scenes"""
        sentences = re.split(r'[.!?]+', script_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_scenes:
            return sentences
        
        scenes = []
        current_scene = []
        current_length = 0
        
        for sentence in sentences:
            current_scene.append(sentence)
            current_length += len(sentence.split())
            
            if current_length >= 20:
                scenes.append(' '.join(current_scene))
                current_scene = []
                current_length = 0
        
        if current_scene:
            scenes.append(' '.join(current_scene))
        
        return scenes[:max_scenes]
    
    def extract_keywords(self, text, max_words=5):
        """Extract keywords"""
        stop_words = ['yang', 'di', 'ke', 'dari', 'dan', 'atau', 'untuk', 'dengan', 'pada', 'ini', 'itu', 'adalah', 'sebuah', 'seorang']
        words = text.split()
        keywords = [w for w in words if w.lower() not in stop_words]
        return ' '.join(keywords[:max_words])
    
    def add_watermark(self, image):
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        bg_width = self.width - 20
        bg_height = 70
        bg_x = 10
        bg_y = self.height - 85
        
        draw.rounded_rectangle([bg_x, bg_y, bg_x + bg_width, bg_y + bg_height], radius=12, fill=(0, 0, 0, 140))
        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image)
        
        lines = self.watermark_text.split("|")
        y = bg_y + 8
        for line in lines:
            line = line.strip()
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x+1, y+1), line, fill="black", font=font)
            draw.text((x, y), line, fill=(255, 255, 255, 220), font=font)
            y += 20
        
        return image.convert("RGB")
    
    def add_text_overlay(self, image, text):
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rectangle([(0, self.height - 250), (self.width, self.height - 85)], fill=(0, 0, 0, 160))
        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        words = text.split()
        lines = []
        current_line = []
        max_chars = 18
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > max_chars:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        y = self.height - 240
        for line in lines[:5]:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x+2, y+2), line, fill="black", font=font)
            draw.text((x, y), line, fill="white", font=font)
            y += 30
        
        image = self.add_watermark(image)
        return image.convert("RGB")
    
    def split_script(self, script, max_duration=90):
        """Split script menjadi parts"""
        words = script.split()
        estimated_duration = len(words) / 2.5
        if estimated_duration <= max_duration:
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
    
    def create_part(self, script, character_prompt, style, part_num):
        print(f"Part {part_num}")
        tts = gTTS(text=script, lang="id", slow=False)
        audio_file = f"{self.output_dir}/temp_part{part_num}.mp3"
        tts.save(audio_file)
        
        audio_clip = AudioFileClip(audio_file)
        duration = audio_clip.duration
        
        # Auto convert ke scenes
        scenes = self.auto_convert_to_scenes(script, max_scenes=4)
        num_scenes = len(scenes)
        
        images = []
        for i, scene_text in enumerate(scenes):
            print(f"  Scene {i+1}/{num_scenes}")
            
            # Extract keywords untuk pencarian
            keywords = self.extract_keywords(scene_text)
            query = f"{keywords} {style} {character_prompt}"
            
            image_paths = self.searcher.get_images_for_scene(
                scene_text, character_prompt, style, num_images=2
            )
            
            if image_paths:
                img = Image.open(image_paths[0])
                img = img.resize((self.width, self.height), Image.LANCZOS)
                img = img.filter(ImageFilter.SHARPEN)
            else:
                img = Image.new("RGB", (self.width, self.height), (30, 30, 50))
            
            img = self.add_text_overlay(img, scene_text)
            images.append(img)
        
        clips = []
        scene_duration = duration / num_scenes
        for img in images:
            clip = ImageClip(np.array(img))
            if MOVIEPY_V2:
                clip = clip.with_duration(scene_duration)
                clip = clip.resized(lambda t: 1 + 0.12*t)
            else:
                clip = clip.set_duration(scene_duration)
                clip = clip.resize(lambda t: 1 + 0.12*t)
            clips.append(clip)
        
        video = concatenate_videoclips(clips, method="compose")
        if MOVIEPY_V2:
            video = video.with_audio(audio_clip)
        else:
            video = video.set_audio(audio_clip)
        
        output_path = f"{self.output_dir}/part_{part_num}.mp4"
        video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", bitrate="800k", preset="ultrafast")
        video.close()
        audio_clip.close()
        
        return output_path
    
    def generate_video(self, script, character_prompt, style="anime"):
        parts = self.split_script(script, self.part_duration)
        video_paths = []
        for i, part_script in enumerate(parts):
            video_path = self.create_part(part_script, character_prompt, style, i+1)
            video_paths.append(video_path)
        return video_paths

def load_story_from_txt(txt_file):
    with open(txt_file, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.strip().split('\n')
    story = {'title': 'Untitled', 'character': 'anime style', 'style': 'anime', 'script': ''}
    script_lines = []
    in_script = False
    for line in lines:
        line = line.strip()
        if line.startswith('JUDUL:'):
            story['title'] = line.replace('JUDUL:', '').strip()
        elif line.startswith('KARAKTER:'):
            story['character'] = line.replace('KARAKTER:', '').strip()
        elif line.startswith('STYLE:'):
            story['style'] = line.replace('STYLE:', '').strip()
        elif line == '---':
            in_script = True
        elif in_script and line:
            script_lines.append(line)
    story['script'] = ' '.join(script_lines)
    return story

def main():
    generator = GoogleImageVideoGenerator(video_quality="360p", part_duration=90, watermark_text="YT: CeritaMistery | Penulis: Yad | Editor: Yad")
    
    stories_dir = "stories"
    if os.path.exists(stories_dir):
        txt_files = [f for f in os.listdir(stories_dir) if f.endswith('.txt')]
        if txt_files:
            all_videos = []
            for txt_file in txt_files:
                story = load_story_from_txt(os.path.join(stories_dir, txt_file))
                videos = generator.generate_video(story['script'], story['character'], story['style'])
                all_videos.extend(videos)
            return all_videos
    
    script = "Di sebuah desa terpencil, terjadi kejadian aneh. Seorang detektif datang untuk mengungkap kebenaran."
    return generator.generate_video(script, "mysterious forest", "mystery")

if __name__ == "__main__":
    main()
