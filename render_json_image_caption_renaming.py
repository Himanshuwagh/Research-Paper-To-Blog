import json
import os
import shutil
import platform

from transformers import pipeline

# Load a summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def rephrase_filename(filename):
    # Remove the extension and summarize the core part of the filename
    summary_filename = summarizer(filename, max_length=10, min_length=5, do_sample=False)[0]["summary_text"]
    return summary_filename


def render_json_image_caption_renaming(pdf_path, output_dir):
    # Extract directory, filename without extension, and extension
    directory, filename = os.path.split(pdf_path)
    base_filename, extension = os.path.splitext(filename)

    # Construct the new path
    json_file_path = os.path.join(directory, f"data{base_filename}.json")

    # Output folder for renamed images
    output_folder = "static"

    # Create output directory if it does not exist
    os.makedirs(output_folder, exist_ok=True)
    
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Ensure the 'static' directory exists
    if not os.path.exists('static'):
        os.makedirs('static')

    # Function to check if the OS supports colons in filenames
    def supports_colons_in_filenames():
        return platform.system() != 'Windows'  # Windows does not support colons in filenames

    # Process figures
    for item in data:
        if item['figType'] == 'Figure':
            # Extract caption for naming
            caption = item['caption']
            
            # Check if the OS supports colons in filenames
            if not supports_colons_in_filenames():
                sanitized_caption = caption.replace(':', '_')  # Replace colon with underscore on Windows
            else:
                sanitized_caption = caption  # Keep the colon for other OSes
            
            sanitized_caption = rephrase_filename(sanitized_caption)

            # Construct the new filename
            new_filename = f"{sanitized_caption}.png"
            
            # Source path
            source_path = item['renderURL']
            
            # Destination path
            dest_path = os.path.join('static', new_filename)
            
            # Copy the file to the new location with the new name
            try:
                shutil.copy(source_path, dest_path)
                print(f"Copied {source_path} to {dest_path}")
            except IOError as e:
                print(f"Unable to copy file. {e}")
            except Exception as e:
                print(f"Unexpected error occurred while copying {source_path}: {e}")

    print("Figure renaming and copying process completed.")