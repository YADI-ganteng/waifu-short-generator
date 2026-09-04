"""Batch Video Generator"""
from waifu_short_generator import WaifuShortGenerator, AnimeStoryGenerator
import time

def batch_generate(count=5, story_type="random", delay=10):
    generator = WaifuShortGenerator()
    videos = []
    for i in range(count):
        print(f"\n🎬 Generating video {i+1}/{count}")
        try:
            story = AnimeStoryGenerator.generate_story(story_type)
            video_path = generator.create_short(
                script=story["script"],
                character_prompt=story["character"],
                style=story["style"],
                filename=f"video_{i+1}.mp4"
            )
            videos.append(video_path)
            print(f"✅ Video {i+1} done!")
            if i < count - 1:
                time.sleep(delay)
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    return videos

if __name__ == "__main__":
    batch_generate(count=5)
