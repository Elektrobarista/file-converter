#This file is part of File-Converter.
#File-Converter is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#File-Converter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with File-Converter. If not, see <https://www.gnu.org/licenses/>.

import json
import os
import csv
import requests
import hashlib
import datetime
import json
import os
import csv
import requests
import hashlib
import datetime

class JsonToCSVConverter:
    def __init__(self, json_filename: str, csv_filename: str = None):
        self.json_filename = json_filename
        self.csv_filename = csv_filename
        self.json_keywords = [] #can be a list or list of lists for nested keywords.
                                #Each list represents the path of a nested keyword with the keyword itself at the last position.
        self.csv_headers = []
        self.query_params = {"downloadformat": "json"}
        self._stored_filename = None
        self._json_path = None
        self._csv_path = None


    def _read_json_file(self) -> dict:
        self._json_path= os.path.realpath(self._stored_filename)
        with open(self._json_path, 'r') as file:
            data = json.load(file)
        return data
    
    def _download_json_file(self, url: str):
        self._json_path= os.path.realpath(self._stored_filename)
        response = requests.get(url)
        with open(self._json_path, mode="wb") as file:
            file.write(response.content)
        
    def _get_file_name(self) -> str:
        # Get the current date and time
        current_datetime = datetime.datetime.now()
        # Convert the date and time to a string
        datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        # Encode the string to bytes
        datetime_bytes = datetime_str.encode('utf-8')
        # Create a SHA-256 hash object
        filename = hashlib.sha256()
        # Update the hash object with the bytes
        filename.update(datetime_bytes)
        filename = f"{filename.hexdigest()}.json"

        return filename
    
    def _get_nested_value(self, item: dict, keys):
            for key in keys:
                if isinstance(item, list):
                    return [self.get_nested_value(i, keys[keys.index(key) + 1:]) for i in item]
                if key in item:
                    item = item[key]
                else:
                    return None
            return item

    def process_json_to_csv(self):
        """
            Process the JSON file and export the data to a CSV file.

            This method takes the JSON file specified by `json_filename` and converts it into a CSV file. If the `json_filename` starts with "http", it is treated as a URL and the file is downloaded. Otherwise, it is assumed to be an uploaded file.

            Returns:
                str: The file path of the generated CSV file.

            Raises:
                FileNotFoundError: If the JSON file specified by `json_filename` does not exist.
                ValueError: If the `json_keywords` or `csv_headers` are empty.

        """

        # check if filename is a URL
        if self.json_filename.startswith("http"):
            self._stored_filename = self._get_file_name()
            self._download_json_file(self.json_filename)
            data = self._read_json_file()     
        else:
        # use the uploaded file
            self._stored_filename = self.json_filename
            data = self._read_json_file()
            self._stored_filename = os.path.basename(self.json_filename)

        # csv_filename need to be a new string without the .json extension in another variable
        self.csv_filename = self._stored_filename.replace(".json", ".csv")
        csv_filepath = os.path.realpath(f"testfiles/converted/{self.csv_filename}")
        with open(csv_filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            # Write column headers as the first row
            writer.writerow(self.csv_headers)
            # Write data from JSON to CSV
            for item in data:
                row_data = [self._get_nested_value(item, keyword) for keyword in self.json_keywords]
                writer.writerow(row_data)

        #write to console. Rewrite when implementing logging with logfile for debugging
        print(f"Data converted from {self.json_filename} to {self._stored_filename} successfully.")

        return csv_filepath

# Placeholder if main function is needed in the future
def main():
    return None

if __name__ == "__main__":
    main()
