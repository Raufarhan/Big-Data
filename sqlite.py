import pandas as pd
import sqlite3  # Tidak perlu install!

# Load CSV
df = pd.read_csv("kurs_data.csv")

# Simpan ke SQLite
conn = sqlite3.connect("kurs.db")  # Akan membuat file 'kurs.db'
df.to_sql("kurs", conn, if_exists="replace", index=False)

print("✅ Data CSV berhasil disimpan ke SQLite!")
conn.close()
