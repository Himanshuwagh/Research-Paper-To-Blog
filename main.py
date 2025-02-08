import openai
import os
from PyPDF2 import PdfReader
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF
from flask import Flask, render_template_string, request, render_template
import markdown2
from pylatexenc.latex2text import LatexNodes2Text
from render_json_image_caption_renaming import render_json_image_caption_renaming
import re
from starlette.staticfiles import StaticFiles

# USER INPUTS + CUSTOMIZATIONS
output_word_limit = 3000
word_limit = output_word_limit * 4


from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
# Flask setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'  # Directory for uploaded files
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF document."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def chunk_text(text, chunk_size=150000, chunk_overlap=8000):
    """Chunks text into smaller segments."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_text(text)


def process_text_with_openai(default_prompt, additional_input_prompt, model="chatgpt-4o-latest", max_tokens=5000):
    """Processes text using OpenAI's API for generating blog content."""
    prompt = default_prompt + additional_input_prompt
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an assistant that creates blog content from research paper approximately around 5000 words."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"An error occurred with OpenAI API: {str(e)}"


def handle_pdf_extraction(pdf_path, additional_input_prompt):
    """Handles PDF extraction and processes text in chunks."""
    pdf_text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(pdf_text)

    full_text = ""
    for chunk in chunks:
        default_prompt = f"""Here is some content: {chunk}. 
                            Write a detailed research blog from this content in LaTeX format. The blog should include:
                            - Inline and display math for equations.
                            - Explanations that make the content accessible to a general audience.
                            Ensure the output adheres to LaTeX syntax and is well-structured."""
        
        processed_chunk_1 = process_text_with_openai(default_prompt, additional_input_prompt)

        # Directory containing the images
        image_directory = "./static/"  # Replace with your directory path

        # Get a list of all PNG files in the directory
        png_files = [f for f in os.listdir(image_directory) if f.endswith('.png')]
        processed_chunk_2 = process_text_with_openai(
            default_prompt=f"""
        I have a blog post: {processed_chunk_1}
        Additionally, I have a list of image file names: {png_files}.

        Please review the blog content carefully and insert placeholders for images. Each placeholder should **only** be the image file name (e.g., `image1.png`) exactly as it appears in the list of file names, with no additional text or formatting.

        - Use the blog content to determine where each image would best enhance the context.
        - Place the image file name as the placeholder directly within the content at the appropriate location.

        Remember: Do not include anything other than the image file name as the placeholder (e.g., no prefixes like 'Fig.' or additional text).
        """,
            additional_input_prompt=additional_input_prompt
        )

        if "An error occurred" not in processed_chunk_2:  # Check if processing was successful
            full_text += processed_chunk_2 + "\n"
        else:
            print(f"Error processing chunk: {processed_chunk_2}")

    return full_text


def latex_to_plain_text(latex_str):
    """Converts LaTeX string to plain text."""
    try:
        return LatexNodes2Text().latex_to_text(latex_str)
    except Exception as e:
        print(f"Error converting LaTeX to text: {e}")
        return "Error: Could not process LaTeX string."


def remove_folder_contents(folder_path):
    """Removes all contents of the specified directory."""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove file or symlink
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove directory and its contents
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


# Directory where the PNG files are stored
directory = './static/'

# List to store image file names
images = []
for filename in os.listdir(directory):
    if filename.endswith(".png"):  # Check if file is a PNG
        images.append(filename)


def extract_figure_number(filename):
    """Extracts figure number from filename."""
    match = re.search(r'(\d+)', filename)  # Look for a number in the filename
    return int(match.group(1)) if match else float('inf')  # Default to inf if no number found


# Sort images based on extracted figure numbers
images.sort(key=extract_figure_number)


def replace_placeholders_with_images(text, images):
    """Replaces image placeholders in text with LaTeX figure environments."""
    updated_text = text
    for i, image in enumerate(images, start=1):
        # Extract image name without extension
        image_name = image.split('/')[-1]  # Extract only the filename
        if not image.startswith("static/"):
            image = f"static/{image}"
        
        caption_image = image_name.split('.')[0]
        if caption_image.endswith('.png'):
            caption_image = caption_image[:-4]
        
        latex_figure = f"""
\\begin{{figure}}[h!]
    \\centering
    \\includegraphics{{{image}}}
    \\caption{{{caption_image}}}
\\end{{figure}}
"""
        
        # Regex pattern to match the image name exactly as it appears in the text (no brackets)
        pattern = rf"(?:\b|[^a-zA-Z0-9]){re.escape(image_name)}(?:\b|[^a-zA-Z0-9])"
        
        # Find all matches to handle cases where the same image might be referenced multiple times
        matches = list(re.finditer(pattern, updated_text))
        if matches:
            for match in matches:
                placeholder = match.group(0)
                updated_text = updated_text.replace(placeholder, latex_figure)
        else:
            print(f"Warning: No placeholder found for image {image_name} with index {i}")

    return updated_text


def extract_latex_content(input_file, output_file):
    """
    Extracts content from \documentclass to \end{document} in a LaTeX file 
    and writes it to a new file while preserving the original format.

    Args:
        input_file (str): Path to the input LaTeX file.
        output_file (str): Path to save the extracted content.
    """
    capture = False
    result = []

    with open(input_file, 'r') as file:
        for line in file:
            if '\\documentclass' in line:
                capture = True
            if capture:
                result.append(line)
            if '\\end{document}' in line:
                break

    # Write the captured content to the output file, preserving formatting
    with open(output_file, 'w') as file:
        file.writelines(result)
    return result


from pdffigures2.pdf import run_pdffigures2

@app.route('/', methods=['GET', 'POST'])
def upload_and_process_pdf():
    """Handles file upload, PDF processing, and content generation."""
    remove_folder_contents('uploads/')
    remove_folder_contents('static/')

    if request.method == 'POST':
        additional_prompt = request.form.get('additional_input_prompt', '')
        if 'file' not in request.files:
            return "No file part in the request"
        file = request.files['file']
        if file.filename == '':
            return "No file selected for uploading"
        if file:
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(pdf_path)
            print(f'pdf_path = {pdf_path}')

            run_pdffigures2(pdf_path, output_dir="./uploads")
            
            render_json_image_caption_renaming(pdf_path, output_dir="./uploads")

            # Process the uploaded file
            processed_text = handle_pdf_extraction(pdf_path, additional_prompt)

            # Replace placeholders with images
            updated_text = replace_placeholders_with_images(processed_text, images)

            # Save the updated text to latex.tex
            with open('latex.tex', 'w', encoding='utf-8') as f:
                f.write(updated_text)

            # Example Usage
            input_file = "latex.tex"
            output_file = "transformed_latex.tex"
            extract_latex_content(input_file, output_file)

            import subprocess

            # Define the command to run
            command = ["pandoc", "transformed_latex.tex", "-s", "--mathjax", "-o", "templates/output.html"]

            try:
                # Execute the command
                subprocess.run(command, check=True)
                print("Pandoc command executed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred: {e}")

        # Render the result page
        return render_template('output.html')
    return render_template('upload.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5600))
    app.run(host='0.0.0.0', port=port)