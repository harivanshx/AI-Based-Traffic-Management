"""
Vehicle Detection Module using YOLOv8
Optimized for CPU-only execution
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent))
import config


class VehicleDetector:
    """
    Detects and tracks vehicles using YOLOv8
    Optimized for CPU performance
    """
    
    def __init__(self):
        """Initialize YOLO model and tracking structures"""
        print(f"[INFO] Initializing YOLOv8 model: {config.YOLO_MODEL}")
        print(f"[INFO] Device: {config.DEVICE} (CPU-only mode)")
        
        # Load YOLO model
        self.model = YOLO(config.YOLO_MODEL)
        
        # Force CPU usage
        self.device = config.DEVICE
        
        # Vehicle tracking
        self.tracked_vehicles = {}
        self.next_vehicle_id = 0
        
        # Statistics
        self.total_detections = 0
        self.fps = 0
        
        print("[INFO] Vehicle detector initialized successfully")
    
    def detect_vehicles(self, frame):
        """
        Detect vehicles in a frame
        
        Args:
            frame: Input image/frame (numpy array)
            
        Returns:
            list: List of detections, each containing:
                  {'bbox': [x1, y1, x2, y2], 'class': str, 'confidence': float, 'id': int}
        """
        start_time = time.time()
        
        # Run YOLO inference (CPU)
        results = self.model.predict(
            frame,
            conf=config.CONFIDENCE_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            imgsz=config.IMG_SIZE,
            device=self.device,
            verbose=False,
            half=False  # Disable half precision for CPU
        )
        
        # Parse results
        detections = []
        
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                # Filter only vehicle classes
                if class_id in config.VEHICLE_CLASSES:
                    detection = {
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'class': config.VEHICLE_CLASSES[class_id],
                        'confidence': confidence,
                        'class_id': class_id,
                        'center': (int((x1 + x2) / 2), int((y1 + y2) / 2))
                    }
                    
                    # Add tracking ID if enabled
                    if config.TRACKING_ENABLED:
                        tracking_id = self._assign_tracking_id(detection)
                        detection['id'] = tracking_id
                    
                    detections.append(detection)
                    self.total_detections += 1
        
        # Calculate FPS
        end_time = time.time()
        self.fps = 1 / (end_time - start_time) if (end_time - start_time) > 0 else 0
        
        return detections
    
    def _assign_tracking_id(self, detection):
        """
        Simple tracking to assign consistent IDs to vehicles
        Uses center point proximity matching
        
        Args:
            detection: Detection dictionary
            
        Returns:
            int: Tracking ID
        """
        center = detection['center']
        bbox = detection['bbox']
        
        # Find closest existing track
        min_distance = float('inf')
        matched_id = None
        
        for vehicle_id, track in list(self.tracked_vehicles.items()):
            # Calculate distance between centers
            track_center = track['center']
            distance = np.sqrt(
                (center[0] - track_center[0])**2 + 
                (center[1] - track_center[1])**2
            )
            
            # Check if within tracking distance
            if distance < config.TRACKING_MAX_DISTANCE and distance < min_distance:
                min_distance = distance
                matched_id = vehicle_id
        
        # Update or create track
        if matched_id is not None:
            # Update existing track
            self.tracked_vehicles[matched_id] = {
                'center': center,
                'bbox': bbox,
                'frames_missing': 0,
                'last_seen': time.time()
            }
            return matched_id
        else:
            # Create new track
            new_id = self.next_vehicle_id
            self.next_vehicle_id += 1
            self.tracked_vehicles[new_id] = {
                'center': center,
                'bbox': bbox,
                'frames_missing': 0,
                'last_seen': time.time()
            }
            return new_id
    
    def cleanup_tracks(self):
        """Remove old tracks that haven't been seen recently"""
        current_time = time.time()
        ids_to_remove = []
        
        for vehicle_id, track in self.tracked_vehicles.items():
            # Remove tracks not seen for N frames
            if current_time - track['last_seen'] > config.TRACKING_MAX_FRAMES_MISSING / 30:  # Assuming ~30 FPS
                ids_to_remove.append(vehicle_id)
        
        for vehicle_id in ids_to_remove:
            del self.tracked_vehicles[vehicle_id]
    
    def get_stats(self):
        """
        Get detection statistics
        
        Returns:
            dict: Statistics including FPS, total detections, active tracks
        """
        return {
            'fps': round(self.fps, 2),
            'total_detections': self.total_detections,
            'active_tracks': len(self.tracked_vehicles)
        }
    
    def draw_detections(self, frame, detections, show_labels=True):
        """
        Draw detection boxes and labels on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            show_labels: Whether to show class labels
            
        Returns:
            frame: Frame with drawn detections
        """
        for detection in detections:
            bbox = detection['bbox']
            vehicle_class = detection['class']
            confidence = detection['confidence']
            
            # Draw bounding box
            color = config.COLORS['GREEN']
            cv2.rectangle(
                frame,
                (bbox[0], bbox[1]),
                (bbox[2], bbox[3]),
                color,
                config.LINE_THICKNESS
            )
            
            # Draw label
            if show_labels:
                label = f"{vehicle_class}: {confidence:.2f}"
                if 'id' in detection:
                    label = f"ID{detection['id']} {label}"
                
                # Background for text
                (text_width, text_height), _ = cv2.getTextSize(
                    label, config.FONT, config.FONT_SCALE, config.FONT_THICKNESS
                )
                cv2.rectangle(
                    frame,
                    (bbox[0], bbox[1] - text_height - 10),
                    (bbox[0] + text_width, bbox[1]),
                    color,
                    -1
                )
                
                # Text
                cv2.putText(
                    frame,
                    label,
                    (bbox[0], bbox[1] - 5),
                    config.FONT,
                    config.FONT_SCALE,
                    config.COLORS['BLACK'],
                    config.FONT_THICKNESS
                )
        
        return frame


# Test function
if __name__ == "__main__":
    print("Testing Vehicle Detector...")
    
    # Initialize detector
    detector = VehicleDetector()
    
    # Test with webcam or video file
    cap = cv2.VideoCapture(0)  # 0 for webcam, or provide video path
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect vehicles
        detections = detector.detect_vehicles(frame)
        
        # Draw detections
        frame = detector.draw_detections(frame, detections)
        
        # Show stats
        stats = detector.get_stats()
        cv2.putText(
            frame,
            f"FPS: {stats['fps']} | Vehicles: {len(detections)}",
            (10, 30),
            config.FONT,
            config.FONT_SCALE,
            config.COLORS['WHITE'],
            config.FONT_THICKNESS
        )
        
        # Display
        cv2.imshow('Vehicle Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
