"""
Quick script to download 4 sample traffic images for testing
These are public domain/free images from direct URLs
"""

import urllib.request
import os

# Create sample_images directory
output_dir = "sample_images"
os.makedirs(output_dir, exist_ok=True)

# Direct image URLs (these are publicly accessible traffic images)
images = {
    "north_high_traffic.jpg": "https://images.pexels.com/photos/210182/pexels-photo-210182.jpeg?auto=compress&cs=tinysrgb&w=800",
    "east_medium_traffic.jpg": "https://images.pexels.com/photos/2255801/pexels-photo-2255801.jpeg?auto=compress&cs=tinysrgb&w=800",
    "south_low_traffic.jpg": "https://images.pexels.com/photos/3119941/pexels-photo-3119941.jpeg?auto=compress&cs=tinysrgb&w=800",
    "west_critical_traffic.jpg": "https://images.pexels.com/photos/2116715/pexels-photo-2116715.jpeg?auto=compress&cs=tinysrgb&w=800"
}

print("=" * 60)
print("DOWNLOADING 4 SAMPLE TRAFFIC IMAGES")
print("=" * 60)
print()

for filename, url in images.items():
    try:
        filepath = os.path.join(output_dir, filename)
        print(f"📥 Downloading: {filename}")
        print(f"   URL: {url[:60]}...")
        
        # Download the image
        urllib.request.urlretrieve(url, filepath)
        
        # Check file size
        size_kb = os.path.getsize(filepath) / 1024
        print(f"   ✓ Saved: {filepath} ({size_kb:.1f} KB)")
        print()
        
    except Exception as e:
        print(f"   ✗ Error downloading {filename}: {str(e)}")
        print()

print("=" * 60)
print("DOWNLOAD COMPLETE!")
print("=" * 60)
print()
print("📁 Images saved to:", os.path.abspath(output_dir))
print()
print("Next steps:")
print("1. Go to http://127.0.0.1:5000")
print("2. Click 'New Simulation'")
print("3. Click 'Select 4 Images' (bulk upload)")
print("4. Navigate to the sample_images folder")
print("5. Select all 4 images")
print("6. Click 'Upload All 4 Images'")
print("7. Click 'Run Simulation'")
print("8. Watch the intersection simulator in action!")
print()
