import sqlite3

db_locale = 'nutrition.db'
conn = sqlite3.connect(db_locale)

c = conn.cursor()

c.execute("""CREATE TABLE food_log (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           name text,
           portion text,
           calories integer,
           description text
)""")


conn.commit()

conn.close()