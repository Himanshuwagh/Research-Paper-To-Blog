# Research Paper to Blog Converter

This project is a Flask-based web application that converts research papers (in PDF format) into detailed blog posts. The application extracts text from the PDF, processes it using OpenAI's GPT-4 model, and generates a well-structured blog post in LaTeX format. The blog post includes inline and display math for equations, making it suitable for technical content. Additionally, the application handles image extraction from the PDF and integrates them into the blog post.

## Features

- **PDF Text Extraction**: Extracts text from uploaded PDF files using `PyMuPDF` (fitz).
- **Text Chunking**: Splits the extracted text into manageable chunks for processing.
- **OpenAI GPT-4 Integration**: Uses OpenAI's GPT-4 model to generate blog content from the extracted text.
- **Image Handling**: Extracts images from the PDF and integrates them into the blog post.
- **LaTeX to HTML Conversion**: Converts the generated LaTeX content into HTML using Pandoc.
- **Web Interface**: Provides a simple web interface for uploading PDFs and viewing the generated blog post.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/research-paper-to-blog.git
   cd research-paper-to-blog
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up OpenAI API Key**:
   - Create a `.env` file in the root directory and add your OpenAI API key:
     ```plaintext
     OPENAI_API_KEY=your_openai_api_key_here
     ```

5. **Install Pandoc**:
   - Ensure Pandoc is installed on your system. You can download it from [Pandoc's official website](https://pandoc.org/installing.html).

## Usage

1. **Run the Flask application**:
   ```bash
   python app.py
   ```

2. **Access the web interface**:
   - Open your web browser and navigate to `http://localhost:5600`.

3. **Upload a PDF**:
   - Use the web interface to upload a research paper in PDF format.
   - Optionally, provide additional prompts to guide the blog generation process.

4. **View the generated blog post**:
   - After processing, the generated blog post will be displayed in HTML format.

## Project Structure

- `app.py`: The main Flask application script.
- `templates/`: Contains HTML templates for the web interface.
  - `upload.html`: The upload page.
  - `output.html`: The page displaying the generated blog post.
- `static/`: Directory for storing static files (e.g., images extracted from PDFs).
- `uploads/`: Directory for storing uploaded PDFs and intermediate files.
- `render_json_image_caption_renaming.py`: Script for handling image extraction and renaming.

## Dependencies

- `Flask`: Web framework for building the application.
- `openai`: Python client for OpenAI's API.
- `PyMuPDF` (fitz): Library for extracting text and images from PDFs.
- `PyPDF2`: Library for reading PDF files.
- `langchain`: Library for text splitting and chunking.
- `pylatexenc`: Library for converting LaTeX to plain text.
- `pandoc`: Tool for converting LaTeX to HTML.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to OpenAI for providing the GPT-4 model.
- Thanks to the developers of `PyMuPDF`, `PyPDF2`, and `langchain` for their excellent libraries.

## Contact

For any questions or feedback, please contact [Your Name] at [your.email@example.com].
