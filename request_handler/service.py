#This file is part of File-Converter.
#File-Converter is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#File-Converter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with File-Converter. If not, see <https://www.gnu.org/licenses/>.
import os
import json
from . import app
from FileConverter import JsonToCSVConverter
from flask import request, jsonify, send_file
from jsonschema import validate
from jsonschema.exceptions import ValidationError

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


# routes
@app.route('/convert/json-to-csv', methods=['POST'])
def handle_payload():
    data = request.get_json()
    schema = load_schema('schema/json_schema.json')
    is_valid, error = validate_data(data, schema)

    if not is_valid:
        return jsonify({"error": error}), 400
    
    converter = JsonToCSVConverter(data['json_file'])
    converter.json_keywords = data['json_keywords']
    converter.csv_headers = data['output_headers']
    file=converter.process_json_to_csv()
    file_path = file

    return send_file(file_path, mimetype='text/csv', as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = JsonToCSVConverter._get_file_name(JsonToCSVConverter)
        file.save(os.path.join("./testfiles/upload", filename))
        return jsonify({"message": f"File {filename} uploaded successfully"}), 200
    return jsonify({"error": "An error occurred while uploading the file"}), 500