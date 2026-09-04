.PHONY: help install download generate batch docker-build docker-run clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make download     - Download model"
	@echo "  make generate     - Generate single video"
	@echo "  make batch        - Generate batch videos"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make clean        - Clean output"

install:
	pip install -r requirements.txt

download:
	python download_model.py

generate:
	python waifu_short_generator.py

batch:
	python batch_generator.py --count 5

docker-build:
	docker build -t waifu-short-generator .

docker-run:
	docker run --gpus all -v $(PWD)/output:/app/output waifu-short-generator

clean:
	rm -rf output/*
	rm -rf __pycache__
	rm -rf *.pyc
