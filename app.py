from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename, safe_join
import os
from io import BytesIO
from glob import glob
from zipfile import ZipFile

app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def rename_files(folder_path): # IMPLEMENT YOUR OWN PROCESSING FUNCTION 
    # List all files in the specified folder
    files = os.listdir(folder_path)

    # Rename files to cardinal numbers
    for i, filename in enumerate(files):
        _, extension = os.path.splitext(filename)
        new_filename = f"{i + 1}{extension}"
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/mainframe')
def mainframe():
    return render_template('MainFrame.html')

@app.route('/mainframe', methods = ['POST'])
def upload_files():
    files = request.files.getlist("file[]")
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Rename files to cardinal numbers
    rename_files(app.config['UPLOAD_FOLDER'])
    
    return redirect(url_for('process_uploads'))

@app.route('/process_uploads')
def process_uploads():
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    # file_count = len(uploaded_files)
    return render_template('process_uploads.html', files=uploaded_files)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('process_uploads'))

# Then, within your view function:
@app.route('/view_file/<filename>')
def view_file(filename):
    safe_filename = secure_filename(filename)
    file_path = safe_join(app.config['UPLOAD_FOLDER'], safe_filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return 'File not found', 404
    
@app.route('/download', methods=['POST'])
def download():
    with ZipFile('archive.zip', 'w') as zipf:
        for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'archive.zip'))
    return send_file('archive.zip', as_attachment=True)

@app.route('/delete_upload', methods=['GET', 'POST'])
def delete_upload():
    print("delete")
    try:
     files = os.listdir(app.config['UPLOAD_FOLDER'])
     for file in files:
       file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
       if os.path.isfile(file_path):
         os.remove(file_path)
     print("All files deleted successfully.")
    except OSError:
     print("Error occurred while deleting files.")
    # Code for the function you want to trigger goes here
    # For example, you can render a template
    return redirect(url_for('index'))

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)