import sqlite3
conn = sqlite3.connect('database/devices.db')
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='devices'")
row = c.fetchone()
print(row[0] if row else 'NOT FOUND')
conn.close()
