import sqlite3
import uuid

#create a data structure
conn = sqlite3.connect('example.db')
c = conn.cursor()

#Create table
c.execute('''Create TABLE if not exists playerCharacters(name TEXT, level INTEGER, classAndLevel TEXT, csheet_id TEXT PRIMARY KEY)''')

try:
    c.execute("INSERT INTO playerCharacters VALUES(?,?,?,?)", ("Siatas Soniathrym",4,"War Wizard 4 Hope Paladin 3 Hexblade Warlock 1","1ze4m1sBRoa9giCweh2onYUpWI2jQz3AHZo1rzPAzqWo"))
    conn.commit()
except sqlite3.IntegrityError as e:
    print(f"The error '{e}' occurred")
    try:
        c.execute("UPDATE playerCharacters SET name = ?, level = ?, classAndLevel = ? WHERE csheet_id = ?",("Siatas Soniathrym",5,"War Wizard 5 Hope Paladin 4 Hexblade Warlock 1","1ze4m1sBRoa9giCweh2onYUpWI2jQz3AHZo1rzPAzqWo"))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"The error '{e}' occurred")

#query database
c.execute("SELECT * FROM playerCharacters")
rows = c.fetchall()
for row in rows:
    print(row)

conn.close()