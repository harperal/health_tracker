import sqlite3

db_locale = 'nutrition.db'
conn = sqlite3.connect(db_locale)

c = conn.cursor()

c.execute("""
SELECT * FROM activity_log
""")

activity_info = c.fetchall()

for activity in activity_info:
    print(activity)

conn.commit()

conn.close()