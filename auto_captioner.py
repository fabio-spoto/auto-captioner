#!/usr/bin/env python3

import os
import subprocess
import math
from datetime import timedelta
from typing import List, Dict
import whisper

class AutoCaptioner:
    def __init__(
        self,
        video_path: str,
        model_size: str = "small",
        max_words: int = 7,
        output_ass: str = None,
        font: str = "Roboto",
        fontsize: int = 42,
        primary_color: str = "&H00FFFFFF",
        secondary_color: str = "&H00FFFF00",
        outline_color: str = "&H00000000",
        outline: int = 2,
        border_style: int = 1,
        shadow: int = 0,
    ):
        self.video_path = video_path
        self.model_size = model_size
        self.max_words = max_words
        base, ext = os.path.splitext(video_path)
        self.output_ass = output_ass or f"{base}_subs.ass"
        self.output_video = f"{base}_output{ext}"
        self.font = font
        self.fontsize = fontsize
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.outline_color = outline_color
        self.outline = outline
        self.border_style = border_style
        self.shadow = shadow
        self.segments: List[Dict] = []
        self.whisper_model = None

    @staticmethod
    def format_ass_time(seconds: float) -> str:
        td = timedelta(seconds=seconds)
        cs = int(td.microseconds / 10000)
        hours = td.seconds // 3600
        mins = (td.seconds % 3600) // 60
        secs = td.seconds % 60
        return f"{hours:d}:{mins:02d}:{secs:02d}.{cs:02d}"

    def load_model(self) -> None:
        self.whisper_model = whisper.load_model(self.model_size)

    def transcribe(self) -> None:
        if not self.whisper_model:
            self.load_model()
        result = self.whisper_model.transcribe(
            self.video_path,
            word_timestamps=True
        )
        self.segments = result.get("segments", [])

    def write_ass(self) -> None:
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: auto
PlayResY: auto

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{self.font},{self.fontsize},{self.primary_color},{self.secondary_color},{self.outline_color},&H00000000,0,0,0,0,100,100,0,0,{self.border_style},{self.outline},{self.shadow},2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        with open(self.output_ass, "w", encoding="utf-8") as f:
            f.write(header)
            for seg in self.segments:
                start = self.format_ass_time(seg["start"])
                end = self.format_ass_time(seg["end"])
                parts = []
                for w in seg.get("words", []):
                    dur_cs = math.ceil((w["end"] - w["start"]) * 100)
                    txt = w["word"].replace("{", "").replace("}", "")
                    parts.append(f"{{\\k{dur_cs}}}{txt}")
                line = " ".join(parts)
                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{line}\n")

    def burn_in_subtitles(self) -> None:
        cmd = [
            "ffmpeg", "-y",
            "-i", self.video_path,
            "-vf", f"ass={self.output_ass}",
            "-c:a", "copy",
            self.output_video
        ]
        subprocess.run(cmd, check=True)

    def run(self) -> None:
        print("1/3: Transcribing with word-level timestamps...")
        self.transcribe()
        print("2/3: Generating ASS file with modern styling...")
        self.write_ass()
        print(f"ASS file created: {self.output_ass}")
        print("3/3: Burning in subtitles with libass...")
        self.burn_in_subtitles()
        print(f"Output video: {self.output_video}")
