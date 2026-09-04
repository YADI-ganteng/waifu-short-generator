"""
🎌 Waifu Short Generator
AI YouTube Shorts Generator dengan WaifuDiffusion
"""

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
from gtts import gTTS
import numpy as np
import random
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WaifuShortGenerator:
    """Generator YouTube Shorts dengan visual anime"""

    def __init__(self, model_path="models/waifu_diffusion", output_dir="output", device=None):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Loading model from {model_path}")
        logger.info(f"Device: {self.device}")

        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None,
            local_files_only=True
        )

        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )
        self.pipe = self.pipe.to(self.device)

        if self.device == "cuda":
            self.pipe.enable_attention_slicing()

        logger.info("✅ Model loaded!")

    def generate_waifu_image(self, prompt, negative_prompt="", width=512, height=768, steps=30):
        """Generate gambar anime"""
        logger.info(f"🎨 Generating: {prompt[:50]}...")

        if not negative_prompt:
            negative_prompt = "low quality, bad anatomy, ugly, deformed, blurry"

        with torch.no_grad():
            image = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=steps,
                guidance_scale=7.5,
                width=width,
                height=height
            ).images[0]

        image = image.resize((1080, 1920), Image.LANCZOS)
        return image

    def add_text_overlay(self, image, text):
        """Tambahkan teks overlay"""
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        draw.rectangle([(0, 1500), (1080, 1920)], fill=(0, 0, 0, 180))
        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        except:
            font = ImageFont.load_default()

        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 15:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        lines.append(" ".join(current_line))

        y = 1550
        for line in lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (1080 - text_width) // 2
            draw.text((x+3, y+3), line, fill="black", font=font)
            draw.text((x, y), line, fill="white", font=font)
            y += 80

        return image.convert("RGB")

    def create_short(self, script, character_prompt, style="anime", language="id", filename=None):
        """Buat video short lengkap"""
        logger.info("🎬 Creating video...")

        tts = gTTS(text=script, lang=language, slow=False)
        audio_file = f"{self.output_dir}/temp_audio.mp3"
        tts.save(audio_file)

        audio_clip = AudioFileClip(audio_file)
        duration = audio_clip.duration

        sentences = [s.strip() for s in script.split(".") if s.strip()]
        num_scenes = min(max(len(sentences), 3), 5)

        images = []
        scene_prompts = [
            f"{character_prompt}, {style}, cinematic, masterpiece",
            f"{character_prompt}, different angle, {style}, dramatic",
            f"{character_prompt}, emotional, {style}, detailed",
            f"{character_prompt}, action pose, {style}, dynamic",
            f"{character_prompt}, peaceful, {style}, beautiful"
        ]

        for i in range(num_scenes):
            prompt = scene_prompts[i % len(scene_prompts)]
            img = self.generate_waifu_image(prompt)

            if i < len(sentences):
                img = self.add_text_overlay(img, sentences[i])

            images.append(img)
            logger.info(f"✅ Scene {i+1}/{num_scenes} done")

        clips = []
        scene_duration = duration / num_scenes

        for img in images:
            clip = ImageClip(np.array(img)).set_duration(scene_duration)
            clip = clip.resize(lambda t: 1 + 0.15*t)
            clips.append(clip)

        video = concatenate_videoclips(clips, method="compose")
        video = video.set_audio(audio_clip)

        if not filename:
            filename = f"waifu_short_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        output_path = f"{self.output_dir}/{filename}"
        video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        video.close()
        audio_clip.close()

        logger.info(f"✅ Video saved: {output_path}")
        return output_path

class AnimeStoryGenerator:
    """Generator cerita anime"""

    STORIES = {
        "fantasy": [
            {
                "script": "Di dunia paralel, seorang gadis menemukan kekuatan tersembunyi. Takdir memanggilnya menjadi pahlawan legendaris.",
                "character": "1girl, silver hair, blue eyes, magical girl, sword",
                "style": "fantasy, epic"
            }
        ],
        "action": [
            {
                "script": "Pertarungan terakhir melawan raja iblis. Kekuatan persahabatan vs kegelapan abadi.",
                "character": "1girl, ninja, katana, battle stance",
                "style": "action, dynamic"
            }
        ],
        "romance": [
            {
                "script": "Pertemuan tak terduga di bawah hujan. Sebuah payung, dua orang, dan awal cerita cinta.",
                "character": "1girl, rain, sharing umbrella, romantic",
                "style": "romance, beautiful"
            }
        ]
    }

    @classmethod
    def generate_story(cls, story_type="random"):
        if story_type == "random":
            story_type = random.choice(list(cls.STORIES.keys()))
        stories = cls.STORIES.get(story_type, cls.STORIES["fantasy"])
        return random.choice(stories)

def main():
    generator = WaifuShortGenerator()
    story = AnimeStoryGenerator.generate_story()
    print(f"📝 Script: {story['script']}")
    print(f"👤 Character: {story['character']}")

    video_path = generator.create_short(
        script=story["script"],
        character_prompt=story["character"],
        style=story["style"]
    )

    print(f"✨ Video created: {video_path}")
    return video_path

if __name__ == "__main__":
    main()
