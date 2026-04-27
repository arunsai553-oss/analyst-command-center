import imageio
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import sys
import os

input_file = "Analyst_Command_Center_Demo.webp"
output_file = "Analyst_Command_Center_Demo.mp4"

try:
    print("Reading WebP frames...")
    reader = imageio.get_reader(input_file)
    frames = []
    for frame in reader:
        frames.append(frame)
    
    print(f"Loaded {len(frames)} frames. Writing MP4...")
    fps = 15  # Browser recording framerate is typically around 15-30
    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile(output_file, codec='libx264', audio=False)
    print(f"Success! {output_file} created.")
except Exception as e:
    print(f"Error: {e}")
