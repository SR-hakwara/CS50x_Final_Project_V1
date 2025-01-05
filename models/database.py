import os
from cs50 import SQL

# Path to the SQLite database file
db_file = "app.db"

# Check if the database file exists
if not os.path.exists(db_file):
    print(f"Database file '{db_file}' does not exist. Creating it...")
    open(db_file, "w").close()  # Create an empty file

# Initialize the SQL object
db = SQL("sqlite:///app.db")