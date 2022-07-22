import sqlite3

db_locale = 'nutrition.db'
conn = sqlite3.connect(db_locale)

c = conn.cursor()

c.execute("""
INSERT INTO activity_log (name, length, calories, description) VALUES
('Walking', '60 mins', 250, 'Leisurely pace to fill up my lunch hour'),
('Elliptical', '30 mins', 320, 'Short elliptical workout before dinner'),
('HIIT', '30 mins', 300, 'Evening workout to get my heart rate up for the day')
""")


conn.commit()

conn.close()