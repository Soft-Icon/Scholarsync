import os, sqlite3, sys
db_path = r"C:\Users\MJ\Desktop\scholarship_platform\\scholarship_platform_backend\\src\\database\\app.db"

print("DB path:", db_path)
print("Exists:", os.path.exists(db_path))
if not os.path.exists(db_path):
    print("Error: DB file not found at that path.")
    sys.exit(1)

print("Size (bytes):", os.path.getsize(db_path))
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables:", tables or "(no tables)")

    for t in tables:
        print("\n--- Table:", t, "---")
        cur.execute("SELECT sql FROM sqlite_master WHERE name = ?", (t,))
        row = cur.fetchone()
        print("Schema:", row[0] if row else "(no schema)")

        cur.execute(f"PRAGMA table_info({t});")
        cols = cur.fetchall()
        print("Columns:", [c[1] for c in cols])

        cur.execute(f"SELECT COUNT(*) FROM {t};")
        cnt = cur.fetchone()[0]
        print("Row count:", cnt)

        cur.execute(f"SELECT * FROM {t} LIMIT 10;")
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print(r)
        else:
            print("(no rows)")
    conn.close()
except sqlite3.DatabaseError as e:
    print("SQLite error:", e)
    sys.exit(1)
except Exception as e:
    print("Error:", e)
    sys.exit(1)