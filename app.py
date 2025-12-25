"""
Flask Web Application for AI Traffic Management System
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
import uuid
import json
from pathlib import Path
import shutil
import cv2
import base64

from web_processor import WebTrafficProcessor

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Change this to a fixed secret in production

# Configuration
UPLOAD_FOLDER = Path('uploads')
RESULTS_FOLDER = Path('uploads/results')
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Create directories
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['RESULTS_FOLDER'] = str(RESULTS_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename, file_type='video'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    elif file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    else:
        return ext in ALLOWED_VIDEO_EXTENSIONS or ext in ALLOWED_IMAGE_EXTENSIONS


def get_session_folder():
    """Get or create session folder"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_folder = UPLOAD_FOLDER / 'sessions' / session['session_id']
    session_folder.mkdir(parents=True, exist_ok=True)
    
    return session_folder


def cleanup_old_sessions():
    """Clean up old session folders (older than 1 hour)"""
    import time
    sessions_folder = UPLOAD_FOLDER / 'sessions'
    
    if not sessions_folder.exists():
        return
    
    current_time = time.time()
    for session_dir in sessions_folder.iterdir():
        if session_dir.is_dir():
            # Check if older than 1 hour
            if current_time - session_dir.stat().st_mtime > 3600:
                shutil.rmtree(session_dir, ignore_errors=True)


@app.route('/')
def index():
    """Main page"""
    # Cleanup old sessions on page load
    cleanup_old_sessions()
    
    # Reset session
    session.pop('session_id', None)
    session.pop('uploaded_files', None)
    session.pop('processing_mode', None)
    
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        direction = request.form.get('direction', '').upper()
        
        if direction not in ['NORTH', 'SOUTH', 'EAST', 'WEST']:
            return jsonify({'error': 'Invalid direction'}), 400
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Determine file type
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        
        if ext in ALLOWED_VIDEO_EXTENSIONS:
            file_type = 'video'
        elif ext in ALLOWED_IMAGE_EXTENSIONS:
            file_type = 'image'
        else:
            return jsonify({'error': 'Invalid file type. Allowed: video (mp4, avi, mov, mkv) or image (jpg, png)'}), 400
        
        # Check consistency with processing mode
        if 'processing_mode' in session:
            if session['processing_mode'] != file_type:
                return jsonify({'error': f'Please upload all {session["processing_mode"]} files'}), 400
        else:
            session['processing_mode'] = file_type
        
        # Save file
        session_folder = get_session_folder()
        direction_folder = session_folder / direction.lower()
        direction_folder.mkdir(exist_ok=True)
        
        filepath = direction_folder / filename
        file.save(filepath)
        
        # Track uploaded files
        if 'uploaded_files' not in session:
            session['uploaded_files'] = {}
        
        session['uploaded_files'][direction] = str(filepath)
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': f'File uploaded for {direction}',
            'direction': direction,
            'filename': filename,
            'file_type': file_type
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process', methods=['POST'])
def process_simulation():
    """Process traffic simulation"""
    try:
        if 'uploaded_files' not in session or not session['uploaded_files']:
            return jsonify({'error': 'No files uploaded'}), 400
        
        uploaded_files = session['uploaded_files']
        processing_mode = session.get('processing_mode', 'video')
        
        # Initialize processor
        processor = WebTrafficProcessor()
        
        # Process each direction
        direction_results = {}
        
        for direction, filepath in uploaded_files.items():
            if processing_mode == 'video':
                result = processor.process_direction_video(filepath, direction)
            else:
                result = processor.process_direction_image(filepath, direction)
            
            direction_results[direction] = result
        
        # Aggregate results
        aggregated = processor.aggregate_results(direction_results)
        
        # Save processed images
        results_folder = RESULTS_FOLDER / session['session_id']
        results_folder.mkdir(parents=True, exist_ok=True)
        
        processed_images = {}
        
        for direction, result in direction_results.items():
            if processing_mode == 'video':
                # Save sample frames
                for idx, frame in enumerate(result.get('sample_frames', [])):
                    output_path = results_folder / f'{direction.lower()}_frame_{idx}.jpg'
                    processor.save_annotated_frame(frame, str(output_path))
                    
                    if idx == 0:  # Use first frame as representative
                        processed_images[direction] = str(output_path)
            else:
                # Save annotated image
                output_path = results_folder / f'{direction.lower()}_annotated.jpg'
                processor.save_annotated_frame(result['annotated_frame'], str(output_path))
                processed_images[direction] = str(output_path)
        
        # Prepare results for display
        results_data = {
            'processing_mode': processing_mode,
            'direction_results': {},
            'recommendations': aggregated['recommendations'],
            'processed_images': processed_images
        }
        
        for direction, result in direction_results.items():
            if processing_mode == 'video':
                results_data['direction_results'][direction] = {
                    'average_vehicles': result['average_vehicles'],
                    'max_vehicles': result['max_vehicles'],
                    'density_level': result['density_level'],
                    'frames_processed': result['total_frames_processed']
                }
            else:
                results_data['direction_results'][direction] = {
                    'vehicle_count': result['vehicle_count'],
                    'density_level': result['density_level']
                }
        
        # Save results to session
        session['results'] = results_data
        session.modified = True
        
        return jsonify({
            'success': True,
            'redirect': url_for('results')
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/results')
def results():
    """Display results page"""
    if 'results' not in session:
        return redirect(url_for('index'))
    
    results_data = session['results']
    
    # Convert images to base64 for display
    images_base64 = {}
    for direction, image_path in results_data['processed_images'].items():
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                images_base64[direction] = f'data:image/jpeg;base64,{img_data}'
    
    results_data['images_base64'] = images_base64
    
    return render_template('results.html', results=results_data)


@app.route('/reset', methods=['POST'])
def reset():
    """Reset session and start new simulation"""
    # Cleanup session folder
    if 'session_id' in session:
        session_folder = UPLOAD_FOLDER / 'sessions' / session['session_id']
        if session_folder.exists():
            shutil.rmtree(session_folder, ignore_errors=True)
        
        results_folder = RESULTS_FOLDER / session['session_id']
        if results_folder.exists():
            shutil.rmtree(results_folder, ignore_errors=True)
    
    # Clear session
    session.clear()
    
    return jsonify({'success': True, 'redirect': url_for('index')})


if __name__ == '__main__':
    print("=" * 60)
    print("AI TRAFFIC MANAGEMENT SYSTEM - WEB INTERFACE")
    print("=" * 60)
    print("\nStarting Flask development server...")
    print("Access the application at: http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
