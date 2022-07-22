import sqlite3

db_locale = 'nutrition.db'
conn = sqlite3.connect(db_locale)

c = conn.cursor()

c.execute("""
SELECT * FROM food_log
""")

food_info = c.fetchall()

for food in food_info:
    print(food)

conn.commit()

conn.close()