#!/usr/bin/env python3

import os
import subprocess
from typing import List, Dict
import whisper

class AutoCaptioner:
    def __init__(
        self,
        video_path: str,
        model_size: str = "small",
        max_words: int = 7,
        output_srt: str = None,
        output_video: str = None,
        font: str = "Arial",
        fontsize: int = 16,
        primary_color: str = "&H00FFFFFF",
        outline_color: str = "&H00000000",
        outline: int = 1,
        border_style: int = 1,
        shadow: int = 0,
    ):
        self.video_path = video_path
        self.model_size = model_size
        self.max_words = max_words
        self.output_srt = output_srt
        base, ext = os.path.splitext(video_path)
        self.output_video = output_video or f"{base}_output{ext}"
        self.font = font
        self.fontsize = fontsize
        self.primary_color = primary_color
        self.outline_color = outline_color
        self.outline = outline
        self.border_style = border_style
        self.shadow = shadow
        self.segments: List[Dict] = []
        self.whisper_model = None
        self.srt_path: str = ""

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        millis = int(seconds * 1000) % 1000
        secs = int(seconds) % 60
        mins = (int(seconds) // 60) % 60
        hours = int(seconds) // 3600
        return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    def load_model(self) -> None:
        self.whisper_model = whisper.load_model(self.model_size)

    def transcribe(self) -> None:
        if self.whisper_model is None:
            self.load_model()
        result = self.whisper_model.transcribe(self.video_path, word_timestamps=True)
        self.segments = result.get("segments", [])

    def write_srt(self) -> None:
        base, _ = os.path.splitext(self.video_path)
        self.srt_path = self.output_srt or f"{base}_sync.srt"
        index = 1
        with open(self.srt_path, "w", encoding="utf-8") as f:
            for seg in self.segments:
                words = seg.get("words", [])
                if not words:
                    continue
                for i in range(0, len(words), self.max_words):
                    chunk = words[i : i + self.max_words]
                    start = chunk[0]["start"]
                    end = chunk[-1]["end"]
                    text = "".join(w["word"] for w in chunk).strip()
                    f.write(f"{index}\n")
                    f.write(f"{self.format_timestamp(start)} --> {self.format_timestamp(end)}\n")
                    f.write(f"{text}\n\n")
                    index += 1

    def build_style(self) -> str:
        return (
            f"FontName={self.font},"
            f"FontSize={self.fontsize},"
            f"PrimaryColour={self.primary_color},"
            f"OutlineColour={self.outline_color},"
            f"Outline={self.outline},"
            f"BorderStyle={self.border_style},"
            f"Shadow={self.shadow}"
        )

    def burn_in_subtitles(self) -> None:
        style = self.build_style().replace("'", "\\'")
        vf_filter = f"subtitles={self.srt_path}:force_style='{style}'"
        cmd = ["ffmpeg", "-y", "-i", self.video_path, "-vf", vf_filter, "-c:a", "copy", self.output_video]
        subprocess.run(cmd, check=True)

    def run(self) -> None:
        print("1/3: Transcribing with word timestamps...")
        self.transcribe()
        print("2/3: Writing SRT file...")
        self.write_srt()
        print(f"SRT created: {self.srt_path}")
        print("3/3: Burning subtitles with style...")
        self.burn_in_subtitles()
        print(f"Finished video: {self.output_video}")