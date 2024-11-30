# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for
import os
import pytesseract
from werkzeug.utils import secure_filename  # Secure filename utility to avoid security risks
from PIL import Image  # Python Imaging Library for image processing

# Specify the path to the Tesseract executable
pytesseract.tesseract_cmd = r"D:\Downloads\tesseract.exe"  # Set path to your Tesseract installation

# Get the current project directory
project_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask application
app = Flask(__name__,
            static_url_path='',  # Set static URL path to empty so we can handle it manually
            static_folder='static',  # Folder for static files (e.g., CSS, JS, images)
            template_folder='templates')  # Folder for HTML templates

# Configure the file upload settings
app.config['UPLOAD_FOLDER'] = 'images'  # Folder to store uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image file extensions

# Ensure the upload folder exists (create it if it doesn't)
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check if the uploaded file has an allowed extension
def allowed_file(filename):
    # Checks if the filename has an extension and if it's in the allowed list
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Class to handle OCR text extraction from an image
class GetText(object):
    def __init__(self, image_path):
        self.image_path = image_path  # Store the path to the image
        self.text = None  # Initialize text attribute to None

    # Method to extract text from the image
    def extract_text(self):
        try:
            # Open the image using Pillow
            image = Image.open(self.image_path)
            # Extract text from the image using Tesseract OCR
            self.text = pytesseract.image_to_string(image)
        except Exception as e:
            # If an error occurs during text extraction, store the error message
            self.text = f"Error extracting text: {str(e)}"
        return self.text  # Return the extracted text (or error message)

# Route for the home page (to upload an image and display extracted text)
@app.route('/', methods=['GET', 'POST'])
def home():
    extracted_text = None  # Initialize extracted_text as None (used for displaying the OCR result)
    
    # Handle POST request (when an image is uploaded)
    if request.method == 'POST':
        # Check if the 'photo' key is in the request files (uploaded file)
        if 'photo' not in request.files:
            return 'No file part', 400  # If no file is uploaded, return an error
        
        # Retrieve the uploaded file from the request
        photo = request.files['photo']
        
        # If the user did not select a file, the filename will be empty
        if photo.filename == '':
            return 'No selected file', 400  # Return error if no file is selected
        
        # Check if the file has a valid extension (png, jpg, jpeg, gif)
        if not allowed_file(photo.filename):
            return 'File type not allowed', 400  # Return error if the file type is not allowed
        
        # Secure the filename to avoid potential security issues (e.g., malicious filenames)
        filename = secure_filename(photo.filename)
        # Generate the full path to save the file in the upload folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # Save the uploaded file to the specified path
        photo.save(filepath)

        # Create an instance of the GetText class, passing the saved image path
        textObject = GetText(filepath)
        # Extract text from the image
        text = textObject.extract_text()

        # Render the template and pass the extracted text and filename to display the results
        return render_template('index.html', extracted_text=text, filename=filename)

    # Handle GET request (when the page is first loaded)
    return render_template('index.html', extracted_text=extracted_text)  # Render page with no extracted text initially

# Run the Flask app in debug mode
if __name__ == '__main__':
    app.run(debug=False)
