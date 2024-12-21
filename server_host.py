import logging
import sys

from flask import Flask, Response, jsonify, abort, request
from werkzeug.exceptions import HTTPException
from pymongo import MongoClient
from gridfs import GridFS
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()
app = Flask(__name__)

# MongoDB setup
MONGO_URI = os.getenv("MONGODB_URL")
DB_NAME = "tuf_repo"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
fs = GridFS(db)

# Configure logging
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))  # Directory of the executable
LOG_FILE = os.path.join(BASE_DIR, "log", "server_host.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('server_host.py')

@app.route("/", methods=["GET"])
def home():
    return jsonify('TUF server')


@app.route('/metadata/<filename>', methods=['GET'])
def get_metadata(filename):
    """
    Retrieve metadata or target files from GridFS.
    """
    try:
        # Check if the requested file is metadata
        is_metadata = filename.endswith(".json")

        # Adjust the lookup path based on the type
        prefix = "metadata" if is_metadata else "targets"
        file = fs.find_one({"filename": f"{prefix}/{filename}"})

        if not file:
            abort(404, description=f"{'Metadata' if is_metadata else 'Target'} file {filename} not found")

        # Set appropriate content type
        content_type = "application/json" if is_metadata else "application/octet-stream"
        return Response(file.read(), content_type=content_type)
    except HTTPException as http_ex:
        # Allow Flask to handle HTTP-related exceptions
        raise http_ex
    except Exception as e:
        logging.exception(f"Unexpected error while fetching file. Error: {str(e)}")
        abort(500, description="Internal server error")


@app.route('/<path:filename>', methods=['GET'])
def get_target(filename):
    """
    Retrieve target files from GridFS.
    """
    logger.info(f"Received request for file: {filename}")
    try:
        file = fs.find_one({"filename": filename})
        if not file:
            logger.error(f"File {filename} not found")
            abort(404, description=f"Target file {filename} not found")
        logger.info(f"File found, returning {filename}")
        return Response(file.read(), content_type="application/octet-stream")

    except HTTPException as http_ex:
        # Allow Flask to handle HTTP-related exceptions
        raise http_ex
    except Exception as e:
        logging.exception(f"Unexpected error while fetching file. Error: {str(e)}")
        abort(500, description=str(e))


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload files to GridFS. Accepts files via form-data.
    """
    try:
        file = request.files['file']
        category = request.form.get('category')  # "metadata" or "targets"
        if category not in ["metadata", "targets"]:
            abort(400, description="Invalid category. Use 'metadata' or 'targets'.")

        if category == "targets":
            file_data = file.read()
            filename = file.filename
            sha256_hash = hashlib.sha256(file_data).hexdigest()
            hash_filename = f"{category}/{sha256_hash}.{filename}"
            fs.put(file_data, filename=hash_filename)
            return jsonify({"message": f"File {file.filename} uploaded to {category}"}), 201

        if category == "metadata":
            file_data = file.read()
            filename = f"{category}/{file.filename}"

            # Check if a file with the same name timestamp.json exists
            existing_file = fs.find_one({"filename": "metadata/timestamp.json"})
            if existing_file:
                logger.info(f"File with filename metadata/timestamp.json already exists. Overwriting...")
                fs.delete(existing_file._id)  # Delete the existing file

            fs.put(file_data, filename=filename)
            return jsonify({"message": f"File {file.filename} uploaded to {category}"}), 201

    except HTTPException as http_ex:
        # Allow Flask to handle HTTP-related exceptions (like abort)
        raise http_ex
    except Exception as e:
        logging.exception(f"Unexpected error while fetching file. Error: {str(e)}")
        abort(500, description=str(e))


@app.route('/repository/info', methods=['GET'])
def repository_info():
    """
    Example endpoint to get repository details.
    """
    info = {
        "name": "TUF Repository with GridFS",
        "description": "A TUF-compliant repository using MongoDB GridFS",
    }
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
