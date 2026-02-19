import torch
from ultralytics import YOLO
import numpy as np
from norfair import Detection, Tracker
from norfair.tracker import TrackedObject
from typing import Union
import cv2
import os

from .utils.repo import RepoManager

class ObjectDetector:

    def __init__(self,
                 model_path: str,
                 repo_manager: Union[RepoManager, None] = None,):
        
        self.model_path = model_path
        self.class_mapping = None
        self.repo_manager = repo_manager
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if "yolo" in model_path.lower() or 'weights' in model_path.lower():
            self.model = YOLO(model_path)
            self.class_mapping = self.model.names
        else:
            raise ValueError("Unsupported model type. Only YOLO models are supported.")

    def detect_real_time(self, tracker: Tracker = None):
        # Open a connection to the webcam (0 is usually the default camera)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open webcam.")

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Perform object detection on the frame
            output_frame, detections = self.detect(frame, visualize=False, tracker=tracker)

            # Display the resulting frame
            cv2.imshow('Real-Time Object Detection', output_frame)

            if self.repo_manager and tracker:
                image_bytes = frame.tobytes()
                h, w, c = frame.shape
                dtype = frame.dtype
                self.repo_manager.manage(detections, image_bytes, self.class_mapping)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the webcam and close windows
        cap.release()
        cv2.destroyAllWindows()

    def detect_image(self, image_path: str, visualize: bool = True):
        image_path_basename = os.path.basename(image_path)
        output_path = os.path.join("output", image_path_basename)
        image = cv2.imread(image_path_basename if 'https' in image_path else image_path)

        # Perform object detection and add to output file
        output_file, detections = self.detect(image, visualize=visualize)

        # Write output file to system
        cv2.imwrite(output_path, output_file)
        return detections

    def detect_video(self, video_path: str, tracker: Tracker = None):
        video_path_basename = os.path.basename(video_path)
        output_path = os.path.join("output", video_path_basename)
        # Set output video writer with codec
        vidcap = cv2.VideoCapture(video_path)
        if not vidcap.isOpened():
            raise RuntimeError(f"Could not open input video: {video_path}")

        w = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
            fps = 25.0

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        if not out.isOpened():
            raise RuntimeError("VideoWriter failed to open. Try a different codec/container.")

        # Read the video
        vidcap = cv2.VideoCapture(video_path)
        frame_read, image = vidcap.read()
        count = 0

        # Iterate over frames and pass each for prediction
        while frame_read:
            # Perform object detection and add to output file
            output_file, _ = self.detect(image, visualize=False, tracker=tracker)

            # Write frame with predictions to video
            out.write(output_file)

            # Read next frame
            frame_read, image = vidcap.read()
            count += 1

        # Release video file when we're ready
        out.release()

    def detect(self, image, visualize=False, tracker=None, conf=0.25, iou=0.7):
        # img_tensor = cv2.resize(image, (640, 640), interpolation=cv2.INTER_LINEAR)
        if 'yolo' in self.model_path.lower() or 'weights' in self.model_path.lower():
            results = self.model.predict(source=image, conf=conf, iou=iou)
            detections = []
            for result in results:
                for box in result.boxes:
                    detection = {
                        'class': box.cls,
                        'confidence': box.conf,
                        'bbox': box.xyxy.tolist()  # [x1, y1, x2, y2]
                    }
                    detections.append(detection)
        else:
            raise ValueError("Unsupported model type. Only YOLO models are supported.")
        print(f"Detections: {detections}")
        if tracker:
            bboxes = [np.array(det['bbox'][0]) for det in detections]
            labels = [int(det['class'].item()) for det in detections]
            scores = [det['confidence'].item() for det in detections]
            dets = [Detection(p, label=label) for p, label, score in zip(bboxes, labels, scores)]
            tracked_objects = tracker.update(detections=dets)
            if tracked_objects:
                detections = tracked_objects
            print(f"Tracked objects: {tracked_objects}")
        output_file = self.visualize_detections(image, detections, visualize=visualize)
        return output_file, detections

    def visualize_detections(self, image, detections, visualize: bool = True):
        for det in detections:
            if isinstance(det, TrackedObject):
                xmin, ymin, xmax, ymax = det.estimate[0]
                score = det.id
                obj_name = self.class_mapping[int(det.label)]
            else:
                xmin, ymin, xmax, ymax = det['bbox'][0]
                score = det["confidence"].item()
                obj_name = self.class_mapping[int(det["class"].item())]
            # Create a Rectangle patch
            xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
            pt1 = (xmin, ymin)  # Top-left corner
            pt2 = (xmax, ymax)  # Bottom-right corner

            # Draw the rectangle
            color = (0, 255, 0)  # BGR color for the box (Green in this case)
            thickness = 2  # Thickness of the box lines in pixels

            cv2.rectangle(image, pt1, pt2, color, thickness)

            # TEXT
            label = f'{obj_name} - {score:.2f}'
            # text_color = (255, 255, 255)
            text_color = (0, 0, 0)
            # Calculate text size and position for the label background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 1
            # Get the width and height of the text box
            (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)

            # Position the label above the bounding box
            label_position = (xmin, ymin - 10 if ymin - 10 > 10 else ymin + text_height + 10)
            label_background_end = (xmin + text_width, label_position[1] - text_height - baseline)

            # Draw the label background (filled rectangle)
            cv2.rectangle(image, label_position, label_background_end, color, -1)

            # Put the text label on the background
            cv2.putText(image, label, (label_position[0], label_position[1] - baseline), font, font_scale, text_color,
                        font_thickness, cv2.LINE_AA)

        # Display the image
        if visualize:
            cv2.imshow("Image with Bounding Box", image)
            cv2.waitKey(0)  # Wait indefinitely until a key is pressed
            cv2.destroyAllWindows()  # Close all OpenCV windows
        return image
