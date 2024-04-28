from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import os
from image_enhancer import enhance_image
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULTS_FOLDER'] = 'results/'

# Configure Flask to serve static files from the 'static' folder
app.static_folder = os.path.join(app.root_path, 'static')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        enhanced_filenames = []

        for file in uploaded_files:
            if file.filename == '':
                continue
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                enhanced_image_path = enhance_image(file_path)
                if enhanced_image_path:
                    enhanced_filename = add_timestamp_to_filename(filename)
                    enhanced_file_path = os.path.join(app.config['RESULTS_FOLDER'], enhanced_filename)
                    os.rename(enhanced_image_path, enhanced_file_path)
                    enhanced_filenames.append(enhanced_filename)

        return render_template('result.html', enhanced_filenames=enhanced_filenames)

    return render_template('index.html')

@app.route('/results/<filename>')
def get_enhanced_image(filename):
    results_folder = app.config['RESULTS_FOLDER']
    return send_from_directory(results_folder, filename)

def add_timestamp_to_filename(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name, ext = os.path.splitext(filename)
    return f"{name}_{timestamp}{ext}"

if __name__ == '__main__':
    app.run(debug=True)
