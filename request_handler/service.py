# This file is part of File-Converter.
# File-Converter is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# File-Converter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with File-Converter. If not, see <https://www.gnu.org/licenses/>.
import io
import json
import uuid
from . import app
from FileConverter import JsonToCSVConverter
from flask import request, jsonify, send_file, make_response
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import hashlib
import sqlite3
from datetime import datetime

# functions
def load_schema(path:str):
    """Load the JSON schema from a file."""
    with open(path) as f:
        return json.load(f)

def validate_data(data, schema):
    """Validate the data against the schema."""
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return False, str(e)
    return True, ""

def store_in_memory(file):
    """Store the file in memory and return its index."""
    in_memory_files.append(file)
    file_index = in_memory_files.index(file)
    return file_index

# store all privacy uploads in memory
in_memory_files = []

def insert_file(file):
    """Insert the file information into the database."""
    conn = sqlite3.connect('./request_handler/file_address.db')
    cursor = conn.cursor()

    # Insert data into the table
    cursor.execute('''
    INSERT INTO file_location (UUID, bytes, hash, listindex, timestamp)
    VALUES (:UUID, :bytes, :hash, :listindex, :timestamp)
    ''', file)

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    print("Data inserted successfully.")

def save_file_reference_to_db(file_id, file_content):
    """Save the file_reference to the database."""
    # Read the content of the file as bytes
    file_content_bytes = file_content.getvalue()

    # Calculate the size of the file
    file_size = len(file_content_bytes)

    # Calculate the hash of the file
    file_hash = hashlib.sha256(file_content_bytes).hexdigest()

    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # store reference to file content in memory
    listindex = store_in_memory(file_content)
   # Insert the file into the database
    file = {
        'UUID': file_id,
        'bytes': file_size,
        'hash': file_hash,
        'listindex': listindex,
        'timestamp': timestamp
    }
    insert_file(file)

# routes

@app.route('/convert/privacy/json-to-csv/<file_id>', methods=['POST'])
def handle_payload_pcy(file_id):
    """Handle the privacy JSON to CSV conversion request."""
    # rewrite for in-memory processing
    data = request.get_json()
    schema = load_schema('schema/json_schema_privacy.json')
    is_valid, error = validate_data(data, schema)

    if not is_valid:
        return jsonify({"error": error}), 400
    
    json_keywords= data['json_keywords']
    csv_headers=data['output_headers']
    if 'download_name' in data:
        download_name = data['download_name']
    else:        
        download_name = 'converted.csv'

    conn = sqlite3.connect('./request_handler/file_address.db')
    cursor = conn.cursor()

    cursor.execute('SELECT listindex FROM file_location WHERE UUID = ?', (file_id,))
    result = cursor.fetchone()
    if result:
        listindex = result[0]
        try:
            file_content = in_memory_files[listindex].getvalue()
        except IndexError:
            return jsonify({"error": "File not found"}), 404
        converter = JsonToCSVConverter(file=file_content, json_keywords=json_keywords, csv_headers=csv_headers)
        csv_file = converter.process_json_to_csv()
        conn.close()
        response = make_response(csv_file)
        response.headers['Content-Disposition'] = f'attachment; filename={download_name}'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
    else:
        conn.close()
        return jsonify({"error": "File not found"}), 404


# Privacy upload endpoint. File is stored in memory and not on disk
@app.route('/privacy/upload', methods=['POST'])
def upload_file_pcy():
    """Handle the privacy file upload request."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_id = str(uuid.uuid4())
        file_content = io.BytesIO(file.read())

        save_file_reference_to_db(file_id, file_content)

        return jsonify({"file_id": file_id}), 200


@app.route('/privacy/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Handle the file download request."""
    conn = sqlite3.connect('./request_handler/file_address.db')
    cursor = conn.cursor()

    cursor.execute('SELECT listindex FROM file_location WHERE UUID = ?', (file_id,))
    result = cursor.fetchone()
    if result:
        listindex = result[0]
        try:
            file_content = in_memory_files[listindex].getvalue()
        except IndexError:
            return jsonify({"error": "File not found"}), 404
        json_file = json.loads(file_content.decode('utf-8'))
        conn.close()
        return json_file, 200
    else:
        conn.close()
        return jsonify({"error": "File not found"}), 404