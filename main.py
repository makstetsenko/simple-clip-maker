import glob

import argparse
from src.clip_builder import build_clip
import logging
import asyncio

movie_formats = ["m4v", "mov", "mp4"]


def get_args():
    parser = argparse.ArgumentParser(description="Script using Stable Diffusion WebUI API.")

    parser.add_argument(
        "--input-dir-path",
        "-i",
        type=str,
        required=True,
        help="Path to the directory with music and video files",
    )
    parser.add_argument(
        "--video-resolution",
        "-r",
        type=str,
        required=False,
        help='Output video resolution. For example "1280x720"',
    )
    parser.add_argument("--fps", "-f", type=str, required=False, help="Output video FPS")

    parser.add_argument(
        "--save-timeline-clips",
        "-st",
        action="store_true",
        required=False,
        help="Save clips that were built for project timeline to output dir",
    )

    parser.add_argument(
        "--debug", "-d", action="store_true", required=False, help="Show segments info on video for adjusting clip"
    )

    return parser.parse_args()


def get_first_path(args, file_ext: list[str]) -> str | None:
    timeline_config_path_templates = [args.input_dir_path.rstrip("/") + "/*." + x for x in file_ext]

    for t in timeline_config_path_templates:
        for g in glob.glob(t):
            return g

    return None


async def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    args = get_args()

    music_path_template = get_first_path(args, file_ext=["mp3", "m4a"])

    video_resolution_items = args.video_resolution.split("x")
    await build_clip(
        audio_file_path_template=music_path_template,
        store_timeline_clips=args.save_timeline_clips,
        video_files_path_template=",".join(
            [args.input_dir_path.rstrip("/") + "/*." + x for x in movie_formats + [f.upper() for f in movie_formats]]
        ),
        video_resolution=(
            int(video_resolution_items[0]),
            int(video_resolution_items[1]),
        ),
        fps=int(args.fps),
        debug=args.debug,
        timeline_config_path=get_first_path(args, file_ext=["yaml", "yml"]),
    )


if __name__ == "__main__":
    asyncio.run(main())
