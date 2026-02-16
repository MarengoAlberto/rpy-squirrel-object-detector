from src import ObjectDetector
from norfair import Tracker
import argparse

from config import settings


# image_path = "https://ultralytics.com/images/bus.jpg"   # Path to the image you want to process
# # video_path = "projet3-input-video.mp4"
# video_path = "dash_cam.mp4"

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', '-s',
                        type=str,
                        help='The source to perform object detection on. The file path of an image or video. Or "webcam" to use the webcam as source.',)
    args = parser.parse_args()
    return args

def main(args):
    model_path = settings.MODEL_PATH
    tracker = Tracker(distance_function=settings.DISTANCE_FUNCTION,
                      distance_threshold=settings.DISTANCE_THRESHOLD,
                      reid_hit_counter_max=settings.REID_HIT_COUNTER_MAX,)
    detector = ObjectDetector(model_path)

    if args.source == "webcam":
        detector.detect_real_time(tracker)
    elif args.source.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        detector.detect_image(args.source)
    elif args.source.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        detector.detect_video(args.source, tracker)
    else:
        print("Please provide a valid source: 'webcam' or a valid image/video file path.")
    # detector.detect_real_time(tracker)
    # detections = detector.detect_image(image_path)
    # detector.detect_video(video_path, tracker)

if __name__ == "__main__":
    args = get_args()
    main(args)
