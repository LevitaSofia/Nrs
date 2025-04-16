import sqlite3

conn = sqlite3.connect('colaboradores.db')
cursor = conn.cursor()

# Get table info
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='colaboradores';")
print("Table Schema:")
print(cursor.fetchone()[0])

# Get a sample row to see the structure
cursor.execute("SELECT * FROM colaboradores LIMIT 1;")
columns = [description[0] for description in cursor.description]
print("\nColumns in table:")
print(columns)

conn.close() 