from setuptools import setup, find_packages

setup(
    name="waifu-short-generator",
    version="1.0.0",
    author="YADI-ganteng",
    description="AI YouTube Shorts Generator dengan WaifuDiffusion",
    url="https://github.com/YADI-ganteng/waifu-short-generator",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "diffusers>=0.21.0",
        "pillow>=10.0.0",
        "moviepy>=1.0.3",
        "gTTS>=2.3.0",
    ],
)
