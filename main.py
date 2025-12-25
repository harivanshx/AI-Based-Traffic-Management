"""
Main Application - AI-Based Traffic Management System
Integrates all modules for real-time traffic control
"""

import cv2
import argparse
import time
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

from vehicle_detector import VehicleDetector
from traffic_analyzer import TrafficAnalyzer
from signal_controller import TrafficSignalController
from visualizer import TrafficVisualizer
import config


class TrafficManagementSystem:
    """
    Main traffic management system integrating all components
    """
    
    def __init__(self, video_source=0, display=True, save_output=False):
        """
        Initialize the traffic management system
        
        Args:
            video_source: Video file path or camera index (0 for webcam)
            display: Whether to show visualization
            save_output: Whether to save output video
        """
        print("="*60)
        print("AI-BASED TRAFFIC MANAGEMENT SYSTEM")
        print("CPU-Optimized Version")
        print("="*60)
        
        self.video_source = video_source
        self.display = display
        self.save_output = save_output
        
        # Initialize video capture
        print(f"\n[INFO] Opening video source: {video_source}")
        self.cap = cv2.VideoCapture(video_source)
        
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video source: {video_source}")
        
        # Get video properties
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 30
        
        print(f"[INFO] Video resolution: {self.frame_width}x{self.frame_height} @ {self.fps} FPS")
        
        # Initialize components
        print("\n[INFO] Initializing system components...")
        self.detector = VehicleDetector()
        self.analyzer = TrafficAnalyzer((self.frame_height, self.frame_width))
        self.controller = TrafficSignalController()
        
        if self.display:
            self.visualizer = TrafficVisualizer()
        
        # Output video writer
        self.video_writer = None
        if self.save_output:
            output_path = Path(config.OUTPUT_PATH)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(output_path),
                fourcc,
                config.OUTPUT_FPS,
                (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
            )
            print(f"[INFO] Saving output to: {output_path}")
        
        # Statistics
        self.frame_count = 0
        self.start_time = time.time()
        self.total_vehicles_detected = 0
        
        print("\n[SUCCESS] System initialized successfully!")
        print("="*60)
        print("\nControls:")
        print("  Press 'q' to quit")
        print("  Press 's' to skip to next signal")
        print("  Press 'p' to pause")
        print("="*60)
    
    def run(self):
        """Main processing loop"""
        paused = False
        frame_skip_counter = 0
        
        try:
            while True:
                if not paused:
                    # Read frame
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        print("\n[INFO] End of video or cannot read frame")
                        break
                    
                    self.frame_count += 1
                    
                    # Frame skipping for better CPU performance
                    frame_skip_counter += 1
                    if frame_skip_counter % config.PROCESS_EVERY_N_FRAMES != 0:
                        continue
                    
                    # Detect vehicles
                    detections = self.detector.detect_vehicles(frame)
                    self.total_vehicles_detected += len(detections)
                    
                    # Analyze traffic
                    traffic_analysis = self.analyzer.analyze_traffic(detections)
                    
                    # Update signal controller
                    signal_status = self.controller.update(traffic_analysis)
                    
                    # Get statistics
                    detector_stats = self.detector.get_stats()
                    
                    stats = {
                        'fps': detector_stats['fps'],
                        'total_vehicles': len(detections),
                        'active_tracks': detector_stats['active_tracks'],
                        'frame_count': self.frame_count
                    }
                    
                    # Visualize
                    if self.display:
                        # Draw detections and zones on frame
                        display_frame = frame.copy()
                        display_frame = self.visualizer.draw_detections_and_zones(
                            display_frame, detections, traffic_analysis
                        )
                        
                        # Create full visualization
                        viz_frame = self.visualizer.create_frame(
                            display_frame, detections, traffic_analysis, 
                            signal_status, stats
                        )
                        
                        # Show
                        self.visualizer.show(viz_frame)
                        
                        # Save if requested
                        if self.video_writer:
                            self.video_writer.write(viz_frame)
                    
                    # Cleanup old tracks periodically
                    if self.frame_count % 30 == 0:
                        self.detector.cleanup_tracks()
                    
                    # Print status to console periodically
                    if self.frame_count % 30 == 0:
                        runtime = time.time() - self.start_time
                        print(f"\r[Frame {self.frame_count}] "
                              f"FPS: {stats['fps']:.1f} | "
                              f"Vehicles: {stats['total_vehicles']} | "
                              f"Signal: {signal_status['active_direction']} ({signal_status['phase']}) | "
                              f"Runtime: {runtime:.1f}s", 
                              end='', flush=True)
                
                # Handle key press
                if self.display:
                    key = self.visualizer.wait_key(1) & 0xFF
                    
                    if key == ord('q'):
                        print("\n\n[INFO] Quit requested by user")
                        break
                    elif key == ord('s'):
                        print("\n[INFO] Skipping to next signal...")
                        self.controller.force_next_signal()
                    elif key == ord('p'):
                        paused = not paused
                        status = "PAUSED" if paused else "RESUMED"
                        print(f"\n[INFO] {status}")
                else:
                    # No display, just a small delay
                    time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\n\n[INFO] Cleaning up...")
        
        # Print final statistics
        runtime = time.time() - self.start_time
        avg_fps = self.frame_count / runtime if runtime > 0 else 0
        
        print("\n" + "="*60)
        print("FINAL STATISTICS")
        print("="*60)
        print(f"Total Runtime: {runtime:.2f} seconds")
        print(f"Frames Processed: {self.frame_count}")
        print(f"Average FPS: {avg_fps:.2f}")
        print(f"Total Vehicles Detected: {self.total_vehicles_detected}")
        print(f"Signal Cycles Completed: {self.controller.cycle_count}")
        print("="*60)
        
        # Release resources
        self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        if self.display:
            self.visualizer.destroy()
        
        print("[SUCCESS] Cleanup complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI-Based Traffic Management System (CPU-Optimized)"
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='0',
        help='Video file path or camera index (default: 0 for webcam)'
    )
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Run without display (headless mode)'
    )
    parser.add_argument(
        '--save-output', '-s',
        action='store_true',
        help='Save output video'
    )
    
    args = parser.parse_args()
    
    # Convert input to int if it's a number (camera index)
    video_source = args.input
    try:
        video_source = int(video_source)
    except ValueError:
        pass  # It's a file path
    
    # Create and run system
    try:
        system = TrafficManagementSystem(
            video_source=video_source,
            display=not args.no_display,
            save_output=args.save_output
        )
        system.run()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
