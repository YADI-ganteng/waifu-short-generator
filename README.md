# 🎌 Waifu Short Generator

AI-powered YouTube Shorts generator menggunakan WaifuDiffusion.

## ✨ Fitur
- Generate gambar anime otomatis
- Text-to-Speech Bahasa Indonesia
- Auto video editing
- Overlay teks otomatis

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
