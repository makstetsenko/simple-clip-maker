import argparse
import src.clip_builder.clip_builder as clip_builder
import glob
import logging

movie_formats = ["m4v", "mov", "mp4", "M4V", "MOV", "MP4"]


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

    return parser.parse_args()


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    args = get_args()
    music_path_template = args.input_dir_path.rstrip("/") + "/*.mp3"

    video_resolution_items = args.video_resolution.split("x")
    clip_builder.build(
        audio_file_path_template=music_path_template,
        store_timeline_clips=args.save_timeline_clips,
        video_files_path_template=",".join([args.input_dir_path.rstrip("/") + "/*." + x for x in movie_formats]),
        video_resolution=(
            int(video_resolution_items[0]),
            int(video_resolution_items[1]),
        ),
        fps=int(args.fps),
    )


try:
    main()
except KeyboardInterrupt:
    pass
