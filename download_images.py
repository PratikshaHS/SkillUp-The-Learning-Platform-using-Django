import os
import requests
from pathlib import Path

# Create the directory if it doesn't exist
image_dir = Path("e:/WindSurf projects/Internship/myproject/static/CoursePlatform/images/courses")
image_dir.mkdir(parents=True, exist_ok=True)

# Image URLs and their corresponding filenames
images = {
    "programming.jpg": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "mathematics.jpg": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "science.jpg": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "business.jpg": "https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "design.jpg": "https://images.unsplash.com/photo-1448375240586-882707db888b?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "language.jpg": "https://images.unsplash.com/photo-1503676260728-1c00da094a0a?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "music.jpg": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "photography.jpg": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "health.jpg": "https://images.unsplash.com/photo-1530026186672-2cd00ffc50fe?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "technology.jpg": "https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&h=400&q=80",
    "education.jpg": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?ixlib=rb-1.2.1&auto=format&fit=crop&w=1600&h=400&q=80"
}

# Download each image
for filename, url in images.items():
    filepath = image_dir / filename
    if not filepath.exists():
        try:
            print(f"Downloading {filename}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Saved {filename}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
    else:
        print(f"{filename} already exists, skipping...")

print("\nAll images have been downloaded successfully!")
