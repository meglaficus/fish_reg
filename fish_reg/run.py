import argparse
import os
from fish_reg.registration import register_video


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    parser.add_argument("-d", "--directory", help="If the filepath is a directory. Defaults to False.",
                        action="store_true", default=False)
    parser.add_argument("-r", "--sampling_rate", help="Set every how many slices to perform registration. Defaults to 3.",
                        default=3, type=int, required=False)
    parser.add_argument("-w", "--smoothing_width", help="Set width of smoothing window. Defaults to 8.",
                        default=8, type=int, required=False)
    parser.add_argument("-sl", "--use_slice", help="If you want to test on only slice of video. Defaults to False.",
                        action="store_true")
    parser.add_argument("-s", "--start_frame", help="Set start frame if using slice. Defaults to 0.",
                        default=0, type=int, required=False)
    parser.add_argument("-e", "--end_frame", help="Set end frame if using slice. Defaults to 100.",
                        default=100, type=int, required=False)

    args = parser.parse_args()

    path = args.filepath
    sampling_rate = args.sampling_rate
    smoothing_width = args.smoothing_width
    use_slice = args.use_slice
    start_frame = args.start_frame
    end_frame = args.end_frame
    directory = args.directory

    if directory:
        for filename in os.listdir(path):
            if filename.endswith(".tif"):
                register_video(os.path.join(path, filename), use_slice,
                               start_frame, end_frame, sampling_rate, smoothing_width)
    else:
        register_video(path, use_slice, start_frame, end_frame,
                       sampling_rate, smoothing_width)


if __name__ == "__main__":
    main()
