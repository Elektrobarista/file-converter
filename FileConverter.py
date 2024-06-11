#This file is part of File-Converter.
#File-Converter is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#File-Converter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with File-Converter. If not, see <https://www.gnu.org/licenses/>.

import io
import json
import csv

class JsonToCSVConverter:
    def __init__(self,file, json_keywords, csv_headers):
        self.file = file
        self.json_keywords = json_keywords #can be a list or list of lists for nested keywords. Each list represents the path of a nested keyword with the keyword itself at the last position.
        self.csv_headers = csv_headers
   
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
        print(f'keyword: {self.json_keywords}')
        print(f'headers: {self.csv_headers}')
        # save json content of file in memory
        data = json.loads(self.file.decode('utf-8'))
        s = io.StringIO()
        writer = csv.writer(s)
        writer.writerow(self.csv_headers)
        for item in data:
            row_data = [self._get_nested_value(item, keyword) for keyword in self.json_keywords]
            print(f'Row data: {row_data}')
            writer.writerow(row_data)    
        s.seek(0)
        csv_string = s.getvalue()
        csv_bytes = csv_string.encode('utf-8')

        return csv_bytes

# Placeholder if main function is needed in the future
def main():
    return None

if __name__ == "__main__":
    main()
