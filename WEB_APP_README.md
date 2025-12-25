# 🌐 Flask Web Interface - AI Traffic Management System

## Overview

A modern web application interface for the AI-Based Traffic Management System. Upload traffic videos or images for each direction (North, South, East, West) and get intelligent traffic signal timing recommendations powered by YOLOv8 computer vision.

## ✨ Features

- **📤 Easy Upload Interface**: Drag-and-drop or click to upload videos/images for each traffic direction
- **🎯 Smart Processing**: Supports both video analysis (multiple frames) and image analysis (single snapshot)
- **📊 Detailed Analytics**: Vehicle counts, traffic density classification, and congestion analysis
- **🚦 Signal Recommendations**: AI-generated optimal traffic light timings based on real-time analysis
- **🎨 Modern UI**: Beautiful, responsive design with traffic-themed colors and smooth animations
- **💾 Session Management**: Automatic cleanup of old uploads and results

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install Flask, Werkzeug, and all existing AI traffic management dependencies.

### 2. Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

### 3. Access the Web Interface

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 📖 How to Use

### Step 1: Upload Files

1. Open the web interface in your browser
2. Upload traffic videos or images for each direction:
   - **North** (↑)
   - **South** (↓)
   - **East** (→)
   - **West** (←)

**Note**: You can upload files for just one direction or all four. The system will process whatever you provide.

**Supported Formats**:
- **Videos**: MP4, AVI, MOV, MKV
- **Images**: JPG, JPEG, PNG, BMP

**Important**: All uploads must be either videos OR images (don't mix both types).

### Step 2: Run Simulation

1. Once you've uploaded at least one file, the "Run Simulation" button will activate
2. Click the button to start processing
3. Wait while the system analyzes the traffic (this may take a few moments)

### Step 3: View Results

The results page will display:

- **📊 Summary**: Overview of processed directions
- **🔄 Optimal Sequence**: Recommended order for green lights (prioritizing congested directions)
- **📈 Per-Direction Analysis**:
  - Vehicle counts (average for videos, total for images)
  - Traffic density level (LOW, MEDIUM, HIGH, CRITICAL)
  - Recommended signal timings (green and yellow durations)
  - Visual detection outputs with bounding boxes

### Step 4: New Simulation

Click "New Simulation" to reset and start analyzing new traffic data.

## 🎯 Processing Modes

### Video Mode
- Processes up to 100 frames per video for efficiency
- Provides average and peak vehicle counts
- Analyzes traffic patterns over time
- Best for: Dynamic traffic analysis

### Image Mode
- Analyzes a single snapshot
- Provides instant vehicle count
- Quick density assessment
- Best for: Real-time snapshots, testing

## 🗂️ Project Structure

```
AI-Based-Traffic-Management-System/
│
├── app.py                      # Flask application (main server)
├── web_processor.py            # Web-specific processing logic
│
├── templates/
│   ├── index.html             # Main upload interface
│   └── results.html           # Results display page
│
├── static/
│   ├── css/
│   │   └── style.css          # Stylesheet (modern design)
│   └── js/
│       └── main.js            # Frontend JavaScript
│
├── uploads/                    # Uploaded files (auto-created)
│   ├── sessions/              # User session data
│   └── results/               # Processed outputs
│
└── src/                       # Core AI modules
    ├── vehicle_detector.py    # YOLOv8 detection
    ├── traffic_analyzer.py    # Traffic analysis
    ├── signal_controller.py   # Signal timing logic
    └── config.py              # Configuration
```

## ⚙️ Configuration

### File Size Limits

Default maximum file size: **500 MB**

To change, edit in `app.py`:
```python
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
```

### Processing Frame Limit

For videos, the system processes up to 100 frames by default.

To change, edit in `web_processor.py`:
```python
def process_direction_video(self, video_path: str, direction: str, max_frames: int = 100)
```

### Traffic Density Thresholds

Edit thresholds in `src/config.py`:
```python
SIGNAL_TIMINGS = {
    'LOW': {'green': 15, 'yellow': 3},      # 0-5 vehicles
    'MEDIUM': {'green': 30, 'yellow': 3},   # 6-15 vehicles
    'HIGH': {'green': 45, 'yellow': 3},     # 16-25 vehicles
    'CRITICAL': {'green': 60, 'yellow': 3}  # 26+ vehicles
}
```

## 🎨 UI Features

- **Dark Mode Theme**: Easy on the eyes with traffic-themed colors
- **Glassmorphism Effects**: Modern translucent cards with backdrop blur
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Hover effects, transitions, and loading indicators
- **Traffic Light Visualization**: Color-coded density badges and signal displays

## 🔧 Troubleshooting

### "Cannot open video"
- Ensure the video format is supported (MP4, AVI, MOV, MKV)
- Try converting the video to MP4 format
- Check that the file isn't corrupted

### "Processing is slow"
- Large video files take longer to process
- System processes up to 100 frames for efficiency
- Consider uploading shorter videos or images for faster results

### "Session expired"
- Sessions are automatically cleaned up after 1 hour
- Your uploaded files may have been deleted
- Start a new simulation

### Port Already in Use
If port 5000 is already in use, change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

## 🔒 Security Notes

**For Production Deployment**:

1. **Set a fixed secret key** in `app.py`:
   ```python
   app.secret_key = 'your-secure-random-key-here'
   ```

2. **Disable debug mode**:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

3. **Use a production server** (e.g., Gunicorn, uWSGI instead of Flask dev server)

4. **Add file upload validation** and virus scanning if exposed to public

5. **Implement user authentication** if handling sensitive traffic data

## 🌟 Features Coming Soon

- [ ] Real-time video streaming
- [ ] Multi-intersection support
- [ ] Historical data tracking
- [ ] Export reports as PDF
- [ ] REST API for integration
- [ ] Mobile app version

## 📝 API Endpoints

### `GET /`
Main upload interface

### `POST /upload`
Upload file for a direction

**Parameters**:
- `file`: File to upload
- `direction`: Direction name (NORTH, SOUTH, EAST, WEST)

### `POST /process`
Process uploaded files and generate recommendations

### `GET /results`
Display analysis results

### `POST /reset`
Reset session and start new simulation

## 💡 Tips for Best Results

1. **Good Lighting**: Ensure videos/images have clear lighting
2. **Clear View**: Camera should have unobstructed view of traffic
3. **Proper Angle**: Overhead or elevated angle works best
4. **Resolution**: Higher resolution provides better detection accuracy
5. **Multiple Frames**: For videos, longer clips provide better analysis

## 🙏 Credits

- **YOLOv8** by Ultralytics for object detection
- **Flask** for web framework
- **OpenCV** for video/image processing
- Original AI Traffic Management System modules

---

**🚦 Smart Traffic Management Made Easy!**
