import os
import subprocess

# --- configuration ---

# input and output base directories
# assumes script runs from the project root
base_media_dir = '_media'

# ffmpeg parameters (optimized for text and solid colors)

# avif: uses libsvtav1. lower crf is higher quality (0 is lossless).
# preset 0 is slowest but gives best compression.
# pix_fmt yuv444p preserves full color data, good for sharp edges.
# avif: use libaom-av1, the reference encoder without dimension limits.
# it is much slower than libsvtav1 but offers great quality and compatibility.
# -crf: quality level (0-63), lower is better. 25 is a good start.
# -cpu-used: speed vs quality trade-off (0-8), higher is faster. 4 is a good balance.
# -row-mt 1: enables row-based multithreading to speed up encoding.
avif_params = [
    "-c:v", "libaom-av1",
    "-crf", "25",
    "-cpu-used", "4",
    "-row-mt", "1",
    "-pix_fmt", "yuv444p"
]

# webp: lossless is often better and smaller for text/graphics.
# preset 'text' is optimized for this type of content.
webp_params = [
    "-c:v", "libwebp",
    "-lossless", "1",
    "-quality", "100",
    "-preset", "text",
    "-vf", "scale=16383:16383:force_original_aspect_ratio=decrease" # hard limit of webp
]

# --- end configuration ---

def create_dir_if_not_exists(directory):
    # creates a directory if it doesn't exist.
    if not os.path.exists(directory):
        print(f"Creating directory: {directory}")
        os.makedirs(directory)

def compress_images(media_subdir):
    # iterates through the png directory and runs compression.
    
    media_dir = os.path.join(base_media_dir, media_subdir)
    # input and output directories
    png_dir = os.path.join(media_dir, "png")
    avif_dir = os.path.join(media_dir, "avif")
    webp_dir = os.path.join(media_dir, "webp")
    
    # ensure output directories exist
    create_dir_if_not_exists(avif_dir)
    create_dir_if_not_exists(webp_dir)

    # check if input directory exists
    if not os.path.isdir(png_dir):
        print(f"Error: Input directory '{png_dir}' not found. Please check the path.")
        return

    # loop through all png files
    for filename in os.listdir(png_dir):
        if filename.lower().endswith(".png"):
            base_name = os.path.splitext(filename)[0]
            input_path = os.path.join(png_dir, filename)
            
            # merge path
            avif_path = os.path.join(avif_dir, f"{base_name}.avif")
            webp_path = os.path.join(webp_dir, f"{base_name}.webp")
            
            # skip if both file exists
            if os.path.isfile(avif_path) and os.path.isfile(webp_path):
                print(f"Info: '{filename}' is converted, skipping.")
                continue
            
            # --- convert to avif ---
            print(f"Converting {filename} to AVIF...")
            
            avif_command = ["ffmpeg", "-i", input_path] + avif_params + [avif_path]
            
            try:
                # run the command
                subprocess.run(avif_command, check=True, capture_output=True, text=True)
                print(f"  -> Successfully saved to {avif_path}")
            except subprocess.CalledProcessError as e:
                print(f"  -> AVIF conversion failed. Error:\n{e.stderr}")
            except FileNotFoundError:
                print("Error: 'ffmpeg' command not found. Please ensure it is installed and in your PATH.")
                return

            # --- convert to webp ---
            print(f"Converting {filename} to WebP...")

            webp_command = ["ffmpeg", "-i", input_path] + webp_params + [webp_path]

            try:
                # run the command
                subprocess.run(webp_command, check=True, capture_output=True, text=True)
                print(f"  -> Successfully saved to {webp_path}")
            except subprocess.CalledProcessError as e:
                print(f"  -> WebP conversion failed. Error:\n{e.stderr}")
            except FileNotFoundError:
                print("Error: 'ffmpeg' command not found. Please ensure it is installed and in your PATH.")
                return
                
    print("\nAll images processed!")

if __name__ == "__main__":

    # iterate subdirs
    for subdir in ["main", "dlc"]:
        compress_images(subdir)
