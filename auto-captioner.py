from typing import List, Dict
import subprocess
import argparse
import whisper
import os


def format_timestamp(seconds: float) -> str:
    millis = int(seconds * 1000) % 1000
    secs = int(seconds) % 60
    mins = (int(seconds) // 60) % 60
    hours = int(seconds) // 3600
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def write_srt_word_aligned(segments: List[Dict], srt_path: str, max_words: int) -> None:
    index = 1
    with open(srt_path, "w", encoding="utf-8") as f:
        for seg in segments:
            words = seg.get("words", [])
            if not words:
                continue
            for i in range(0, len(words), max_words):
                chunk = words[i:i + max_words]
                start = chunk[0]["start"]
                end = chunk[-1]["end"]
                text = "".join(w["word"] for w in chunk).strip()
                f.write(f"{index}\n")
                f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
                f.write(f"{text}\n\n")
                index += 1


def transcribe_and_save_srt(video_path: str, model_size: str, max_words: int, output_srt: str = None) -> str:
    model = whisper.load_model(model_size)
    result = model.transcribe(video_path, word_timestamps=True)
    segments = result.get("segments", [])
    base, _ = os.path.splitext(video_path)
    srt_path = output_srt or f"{base}_sync.srt"
    write_srt_word_aligned(segments, srt_path, max_words)
    return srt_path


def burn_in_subtitles(video_path: str, srt_path: str, output_path: str, style: str) -> None:
    safe_style = style.replace("'", "\\'")
    vf_filter = f"subtitles={srt_path}:force_style='{safe_style}'"
    cmd = ["ffmpeg", "-y", "-i", video_path, "-vf", vf_filter, "-c:a", "copy", output_path]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Transcribe a video using Whisper and burn-in word-aligned subtitles.")
    parser.add_argument("video", help="Path to input video file")
    parser.add_argument("-m", "--model", default="small", choices=["tiny","base","small","medium","large"], help="Whisper model size to use (default: small)")
    parser.add_argument("-w", "--max-words", type=int, default=7, help="Maximum words per subtitle chunk (default: 7)")
    parser.add_argument("-o", "--output", help="Path to output video (default: <input>_output.mp4)")
    parser.add_argument("--srt", help="Custom output path for generated .srt file")
    parser.add_argument("--font", default="Arial", help="Font name (default: Arial)")
    parser.add_argument("--fontsize", type=int, default=16, help="Font size (default: 16)")
    parser.add_argument("--primary-color", default="&H00FFFFFF", help="Primary color in ASS format (default: &H00FFFFFF)")
    parser.add_argument("--outline-color", default="&H00000000", help="Outline color in ASS format (default: &H00000000)")
    parser.add_argument("--outline", type=int, default=1, help="Outline thickness (default: 1)")
    parser.add_argument("--border-style", type=int, default=1, help="Border style (default: 1)")
    parser.add_argument("--shadow", type=int, default=0, help="Shadow depth (default: 0)")

    args = parser.parse_args()
    video_path = args.video
    base, ext = os.path.splitext(video_path)
    output_video = args.output or f"{base}_output{ext}"

    print("1/3: Transcribing with word timestamps...")
    srt_file = transcribe_and_save_srt(video_path, args.model, args.max_words, args.srt)
    print(f"SRT created: {srt_file}")

    style = (
        f"FontName={args.font},"
        f"FontSize={args.fontsize},"
        f"PrimaryColour={args.primary_color},"
        f"OutlineColour={args.outline_color},"
        f"Outline={args.outline},"
        f"BorderStyle={args.border_style},"
        f"Shadow={args.shadow}"
    )

    print("2/3: Burning subtitles with style...")
    burn_in_subtitles(video_path, srt_file, output_video, style)
    print(f"Finished video: {output_video}")


if __name__ == "__main__":
    main()
