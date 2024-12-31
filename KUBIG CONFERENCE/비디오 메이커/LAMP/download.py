import os
import requests


file_links = [
    "152ZEdQPJIJBSy9XUyVLjkz183HIsa5_1", 
    "1wZsYspFrdHWfamwRVGrSq8puqgUXihpu", 
    "1I9-_2x0yfbr8-OX6v-eJpmZWjT3APsqL", 
    "14cPvp_melveFxDNbUpIJxy2ClpbH2VPj", 
    "1Ve1MSRC42cZ4LvWAe7AnCtBiRAmNtIlO", 
    "16jAeha79XbCqh2Vw0RpDsFz959C0hqJa", 
    "1pFoEIoHXF87iw1bF0ujcax963f-kiZp5", 
    "1JT8JatF-iBwGCxpNFxamNT4HbMLwjIhZ", 
]


os.makedirs("training_video", exist_ok=True)


for i, file_id in enumerate(file_links, start=1):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    output_path = f"training_video/video_{i}.mp4"
    
    print(f"Downloading video {i} to {output_path}...")
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(output_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Video {i} downloaded successfully.")
    else:
        print(f"Failed to download video {i}. Status code: {response.status_code}")
