import sqlite3

db_locale = 'nutrition.db'
conn = sqlite3.connect(db_locale)

c = conn.cursor()

c.execute("""
DROP TABLE food_log
""")


conn.commit()

conn.close()