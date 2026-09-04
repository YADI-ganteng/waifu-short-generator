"""Download WaifuDiffusion model"""
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import os

def download_model(model_id="hakurei/waifu-diffusion", save_path="models/waifu_diffusion"):
    print(f"📥 Downloading {model_id}...")
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        safety_checker=None
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    os.makedirs(save_path, exist_ok=True)
    pipe.save_pretrained(save_path)
    print(f"✅ Model saved to: {save_path}")

if __name__ == "__main__":
    download_model()
