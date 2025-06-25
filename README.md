# Auto Captioner – Automatically Create Subtitles With Whisper
Automated Python CLI tool for transcribing videos with OpenAI Whisper, creating word-aligned SRT subtitles, and stylized embedding into the video via FFmpeg.

## Showcase

### Before
![before](https://raw.githubusercontent.com/fabio-spoto/auto-captioner/refs/heads/main/showcase/before.png)

### After
![after](https://raw.githubusercontent.com/fabio-spoto/auto-captioner/refs/heads/main/showcase/after.png)

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

## Donation
### Please donate this project because it is free!
<a href="https://buymeacoffee.com/fabiospoto" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>
