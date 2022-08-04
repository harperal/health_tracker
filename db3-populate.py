import sqlite3

db_locale = 'nutrition.db'
conn = sqlite3.connect(db_locale)

c = conn.cursor()

c.execute("""
INSERT INTO cal_goal (calories) VALUES
(2000)
""")


conn.commit()

conn.close()