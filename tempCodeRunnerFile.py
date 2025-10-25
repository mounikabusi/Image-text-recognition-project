from flask import Flask, request, render_template
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

def preprocess_image(image):
    # Convert PIL image to NumPy array
    img_array = np.array(image)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    
    # Detect skew angle and correct it
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = thresh.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    # Convert back to PIL image
    preprocessed_image = Image.fromarray(rotated)
    return preprocessed_image

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error='No selected file')

    try:
        # Open image using PIL
        image = Image.open(io.BytesIO(file.read()))
        
        # Preprocess image
        preprocessed_image = preprocess_image(image)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(preprocessed_image)
        if not text.strip():
            text = 'No text extracted.'
        
        return render_template('index.html', result=text)
    except Exception as e:
        return render_template('index.html', error=f'Error: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True)

