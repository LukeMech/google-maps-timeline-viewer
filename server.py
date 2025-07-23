from flask import Flask, request, abort, Response, jsonify, send_file
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get API key and token
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
secret_token = os.getenv("SECRET_TOKEN")
secret_token_files = os.getenv("SECRET_TOKEN_FILES")
BASE_FILES_DIR = "files"

app = Flask(__name__)

@app.route('/')
def index():
    token = request.args.get('token')
    if token != secret_token:
        abort(403)  # Forbidden

    try:
        with open("timeline.html", "r", encoding="utf-8") as file:
            content = file.read()
            content = content.replace('window.GOOGLE_MAPS_API_KEY = "YOUR_API_KEY"', 'window.GOOGLE_MAPS_API_KEY = "' + google_maps_api_key + '"')
            content = content.replace('MY_SECRET_FILES_TOKEN', secret_token_files)
            return Response(content, mimetype='text/html')
    except FileNotFoundError:
        abort(404)

@app.route('/files/', defaults={'subpath': ''})
@app.route('/files/<path:subpath>')
def serve_files(subpath):
    token = request.args.get('token')
    if token != secret_token_files:
        abort(403)  # Forbidden

    # Build the full filesystem path based on the requested subpath
    fs_path = os.path.normpath(os.path.join(BASE_FILES_DIR, subpath))

    if os.path.isdir(fs_path):
        # If the path is a directory, serve the index.json file inside that directory
        index_json_path = os.path.join(fs_path, "index.json")
        if os.path.isfile(index_json_path):
            return send_file(index_json_path, mimetype='application/json')
        else:
            # Optionally, you could generate the file list dynamically here:
            # files_list = [f for f in os.listdir(fs_path) if os.path.isfile(os.path.join(fs_path, f))]
            # return jsonify(files_list)

            abort(404)  # index.json not found
    elif os.path.isfile(fs_path):
        # If the path is a file, serve the file directly
        return send_file(fs_path)
    else:
        abort(404)  # Path does not exist

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7998)
