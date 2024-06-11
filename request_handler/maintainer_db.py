#This file is part of File-Converter.
#File-Converter is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#File-Converter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with File-Converter. If not, see <https://www.gnu.org/licenses/>.
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Path to your SQLite database file
db_path = './request_handler/file_address.db'

# Read the threshold minutes from the .env file
threshold_minutes = int(os.getenv('TRESHOLD_MINUTES'))

# Calculate the threshold datetime
threshold_datetime = datetime.now() - timedelta(minutes=threshold_minutes)

# Convert the threshold datetime to a string format if needed (e.g., 'YYYY-MM-DD HH:MM:SS')
threshold_datetime_str = threshold_datetime.strftime('%Y-%m-%d %H:%M:%S')

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Execute the SQL command to delete old entries
delete_query = """
DELETE FROM file_location
WHERE strftime('%Y-%m-%d %H:%M:%S', timestamp) < strftime('%Y-%m-%d %H:%M:%S', ?);
"""
cursor.execute(delete_query, (threshold_datetime_str,))

# Commit the changes and close the connection
conn.commit()
conn.close()
