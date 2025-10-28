from flask import Flask, request, render_template
import pytesseract
from PIL import Image
import io

app = Flask(__name__)

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
        image = Image.open(io.BytesIO(file.read()))
        text = pytesseract.image_to_string(image)
        if not text.strip():
            text = 'No text extracted.'
        return render_template('index.html', result=text)
    except Exception as e:
        return render_template('index.html', error=f'Error: {str(e)}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
