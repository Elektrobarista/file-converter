#This file is part of File-Converter.
#File-Converter is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#File-Converter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with File-Converter. If not, see <https://www.gnu.org/licenses/>.
import sqlite3

def create_table():
    # Connect to SQLite database
    conn = sqlite3.connect('./request_handler/file_address.db')
    cursor = conn.cursor()

    # Create table with the specified columns
    cursor.execute('''
    CREATE TABLE file_location (
        id INTEGER PRIMARY KEY,
        UUID TEXT NOT NULL,
        bytes INTEGER,
        hash TEXT NOT NULL,
        listindex Integer,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

    # Provide a confirmation message
    return "Database and table created successfully."

if __name__ == "__main__":
    print(create_table())
