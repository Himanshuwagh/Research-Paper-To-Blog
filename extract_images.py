import fitz  # PyMuPDF
from PIL import Image
import io
import re

def extract_images_with_captions(pdf_path):
    """
    Extracts images from a PDF, attempts to find their captions, and saves them with a filename based on the caption or 'unnamed' if no caption is found.

    Args:
    pdf_path (str): Path to the PDF file.

    Returns:
    None
    """
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    # Regular expression to match captions like "Figure 1: The Transformer - model architecture"
    caption_pattern = re.compile(r'Figure \d+: (.+)')

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract images from this page
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Load image into memory
            image = Image.open(io.BytesIO(image_bytes))
            
            # Try to find a caption for this image
            caption = None
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block.get("type") == "text":
                    for line in block["lines"]:
                        for span in line["spans"]:
                            match = caption_pattern.search(span["text"])
                            if match:
                                caption = match.group(1).strip()
                                # Assuming the caption is close to the image's position
                                if abs(span["bbox"][0] - img["bbox"][0]) < 100:  # Adjust this threshold as necessary
                                    break
                    if caption:
                        break
            
            # Use "unnamed" if no caption found
            if not caption:
                caption = f"unnamed_{page_num}_{img_index}"
            
            # Clean up the caption for use in filename
            filename = caption.replace(' ', '_').replace('/', '_').replace('\\', '_')
            save_path = f"{filename}.png"
            
            # Save the image with the cleaned caption or 'unnamed' as the filename
            image.save(save_path, "PNG")
            print(f"Saved image as {save_path}")

    doc.close()