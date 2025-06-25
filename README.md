# Auto Captioner – Automatically Create Subtitles With Whisper
Automated Python CLI tool for transcribing videos with OpenAI Whisper, creating word-aligned SRT subtitles, and stylized embedding into the video via FFmpeg.

## Installation
### Make sure you have the right python version
> python 3.9.0 or lower version are needed
### Clone the project
```
git clone https://github.com/fabio-spoto/auto-captioner.git
```
### Install all python packages
```
pip install -r requirements.txt
```

## Get Started
### Generate video
```
python auto-captioner.py video.mp4
```
### Set specific whisper model (default is small)
```
python auto-captioner.py video.mp4 --model large
```
### See options with help command
```
python auto-captioner.py -h
```
