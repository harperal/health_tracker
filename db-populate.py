import sqlite3

db_locale = 'nutrition.db'
conn = sqlite3.connect(db_locale)

c = conn.cursor()

c.execute("""
INSERT INTO food_log (name, portion, calories, description) VALUES
('Wheat Toast', '1 slice', 90, 'Wheat Toast was delicious and filling'),
('Eggs', '2 eggs', 180, 'Eggs were filling and kept me satiated'),
('Coffee', '1.5 cups', 6, 'Coffee is a nice pick me up in the morning')
""")


conn.commit()

conn.close()