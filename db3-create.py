import sqlite3

db_locale = 'nutrition.db'
conn = sqlite3.connect(db_locale)

c = conn.cursor()

c.execute("""CREATE TABLE cal_goal (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           calories integer
)""")


conn.commit()

conn.close()