import argparse
import src.plot_builder as plot_builder
import src.clip_builder as clip_builder
import glob


def get_args():
    parser = argparse.ArgumentParser(description="Script using Stable Diffusion WebUI API.")

    parser.add_argument("--music-file", "-m", type=str, required=True, help='Path to the music file')
    parser.add_argument("--video-files-path-template", "-v", type=str, required=False, help="Template to video files. For example './videos/*.mp4' or './videos/*.*' or './videos/my-video.mp4'")
    parser.add_argument("--plot", "-p", action="store_true", required=False, help="Build peaks plot to investigate them")
    parser.add_argument("--store-sub-clips", action="store_true", required=False, help="Build peaks plot to investigate them")

    return parser.parse_args()


def main():
    args = get_args()
    
    music_file_path = glob.glob(args.music_file)[0]
    
    if args.plot:
        plot_builder.build_plot(music_file_path)
        return

    clip_builder.build_music_clip(args)


try:
    main()
except KeyboardInterrupt:
    pass