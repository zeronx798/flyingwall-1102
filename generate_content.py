import os
import re

# --- configuration ---

readme_file = "README.md"
png_dir = "_media/png"

start_marker = "<!-- START GENERATE -->"
end_marker = "<!-- END GENERATE -->"

# --- end configuration ---

def natural_sort_key(s):
    # this key allows for sorting strings in a natural, human-friendly order.
    # e.g., '2.png' comes before '10.png'.
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def update_readme():
    # check if the png directory exists.
    if not os.path.isdir(png_dir):
        print(f"Error: Directory not found at '{png_dir}'")
        return

    # get and sort all png files.
    try:
        png_files = [f for f in os.listdir(png_dir) if f.lower().endswith(".png")]
        png_files.sort(key=natural_sort_key)
    except FileNotFoundError:
        print(f"Error: Could not list files in '{png_dir}'.")
        return
        
    if not png_files:
        print(f"Warning: No PNG files found in '{png_dir}'.")
        # we can still clean up the readme content
        html_to_insert = ""
    else:
        print(f"Found {len(png_files)} PNG files. Generating HTML...")
        picture_blocks = []
        for filename in png_files:
            base_name = os.path.splitext(filename)[0]
            block = (
                '<picture>\n'
                f'  <source srcset="_media/avif/{base_name}.avif" type="image/avif">\n'
                f'  <source srcset="_media/webp/{base_name}.webp" type="image/webp">\n'
                f'  <img src="_media/png/{base_name}.png" alt="{base_name}">\n'
                '</picture>'
            )
            picture_blocks.append(block)
        
        # join all blocks with a newline in between.
        html_to_insert = "\n".join(picture_blocks)

    # read the readme file.
    try:
        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {readme_file} not found.")
        return

    # create the regex pattern to find the content between markers.
    # re.DOTALL makes '.' match newlines as well.
    pattern = re.compile(f"{start_marker}(.*?){end_marker}", re.DOTALL)

    # check if the markers exist in the file.
    if not pattern.search(content):
        print(f"Error: Markers '{start_marker}' and '{end_marker}' not found in {readme_file}.")
        return

    # prepare the new content to be inserted.
    # we add newlines for clean formatting in the markdown file.
    replacement_block = f"{start_marker}\n{html_to_insert}\n{end_marker}"
    
    # replace the old content with the new block.
    new_content = pattern.sub(replacement_block, content)

    # write the updated content back to the readme file.
    try:
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully updated {readme_file}.")
    except IOError as e:
        print(f"Error: Could not write to {readme_file}. Details: {e}")


if __name__ == "__main__":
    update_readme()
