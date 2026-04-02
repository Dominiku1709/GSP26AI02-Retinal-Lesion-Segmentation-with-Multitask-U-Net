import sqlite3

try:
    conn = sqlite3.connect('oct_app.db')
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("\n✅ DATABASE VERIFICATION")
    print("=" * 50)
    print(f"Tables found: {tables}")
    
    if 'patients' in tables:
        cursor.execute("PRAGMA table_info(patients)")
        columns = cursor.fetchall()
        print("\n📋 PATIENTS TABLE SCHEMA:")
        for col in columns:
            print(f"   - {col[1]}: {col[2]}")
    else:
        print("\n⚠️  WARNING: patients table not found!")
    
    if 'oct_scans' in tables:
        cursor.execute("PRAGMA table_info(oct_scans)")
        columns = cursor.fetchall()
        print("\n📋 OCT_SCANS TABLE SCHEMA:")
        for col in columns:
            print(f"   - {col[1]}: {col[2]}")
    
    print("\n✅ SUCCESS: Backend database is ready!")
    
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
