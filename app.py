from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
from PIL import Image
import imagehash
import gcs


app = Flask(__name__)

## Globals ##
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024  # 256 MB
app.config['UPLOAD_FOLDER'] = "uploads/"
app.config['GCS_UPLOAD'] = False

ALLOWED_EXTENSIONS = {'png', '.jpg', '.jpeg','gif', '.heic', '.heif', '.webp', '.tif', '.tiff', '.raw', '.bmp', '.pdf', '.mpeg', '.mpg', '.ogg', '.mp4', '.avi', '.mov', ''}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def home():
    return 'Hello, Flask!'

@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            longFileName = prepareFileName(secure_filename(file.filename))
            filename = longFileName.split(app.config['UPLOAD_FOLDER'], 1)[1]
            print(f'Trying to save file: {secure_filename(file.filename)} as: {longFileName}, {type(longFileName)}')
            file.save(longFileName)
            print('File uploaded successfully')
            with Image.open(file) as image:
                print(imagehash.average_hash(image))
            with Image.open(longFileName) as imageFile:
                print(imagehash.average_hash(imageFile))     
            # except:
            #     return f'Error saving file: ', 500
            if app.config['GCS_UPLOAD']:
                gcs.uploadFile(longFileName, f'testFolder/{filename}')
                print(f'GCS: {filename}')
                return 'File Successfully Uploaded to GCS'
            return 'File Successfully Uploaded'
        elif 'file' not in request.files:
            return 'No file part in the request', 400
        elif file and not allowed_file(file.filename):
            return 'This File type is not allowed', 400

    return 'No file uploaded'

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return 'File is too large', 413

def prepareFileName(fileExists, iter=1):
    if not app.config['UPLOAD_FOLDER'] in fileExists:
        fileExists = os.path.join(app.config['UPLOAD_FOLDER'], fileExists)
    print("Starting File Check")
    print(os.path.isfile(fileExists))
    if not os.path.isfile(fileExists):
        print('return')
        print(f'return:{fileExists}')
        return fileExists
    print('File exists')
    baseFile = f'{fileExists.rsplit(".", 1)[0].lower()}'
    fileExt = f'.{fileExists.rsplit(".", 1)[1].lower()}'
    print(baseFile)
    print(f'-{iter}')
    if f'-{iter}' in baseFile:
        print("iter found")
        baseFile = f'{baseFile.rsplit("-", 1)[0]}'
        iter = iter + 1
        print(f'Base File Name: {baseFile}')
    fileExists = f'{baseFile}-{iter}{fileExt}'
    print(f'New Filename: {fileExists}')
    return prepareFileName(fileExists, iter)



if __name__ == '__main__':
    app.run(debug=True)