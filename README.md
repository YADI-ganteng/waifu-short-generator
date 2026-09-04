# 🎌 Waifu Short Generator

AI-powered YouTube Shorts generator menggunakan WaifuDiffusion.

## ✨ Fitur Utama
- 🎨 Auto-generate anime images
- 🔊 Text-to-Speech Bahasa Indonesia
- 🎬 Auto video editing
- 📝 Overlay teks otomatis
- 🚀 Batch processing
- 🐳 Docker support
- ⚡ GitHub Actions

## 🛠️ Installation
```bash
git clone https://github.com/YADI-ganteng/waifu-short-generator.git
cd waifu-short-generator
pip install -r requirements.txt
python download_model.py
```

## 🚀 Quick Start
```python
from waifu_short_generator import WaifuShortGenerator

generator = WaifuShortGenerator()
generator.create_short(script="Cerita kamu...", character_prompt="1girl, anime")
```

## 📝 License
MIT License
