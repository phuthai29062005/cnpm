from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        print("--- BAT DAU DON DEP DATABASE ---")
        
        # 1. Xóa nốt các FK còn sót (cho chắc chắn)
        try:
            rows = conn.execute(text("SELECT name, OBJECT_NAME(parent_object_id) FROM sys.foreign_keys")).fetchall()
            for fk, table in rows:
                conn.execute(text(f"ALTER TABLE {table} DROP CONSTRAINT {fk}"))
                print(f"Da xoa FK: {fk}")
        except Exception as e:
            print(f"Loi xoa FK: {e}")

        # 2. Xóa các bảng
        try:
            rows = conn.execute(text("SELECT name FROM sys.tables")).fetchall()
            for (table,) in rows:
                if table != 'sysdiagrams':
                    conn.execute(text(f"DROP TABLE {table}"))
                    print(f"Da xoa bang: {table}")
        except Exception as e:
            print(f"Loi xoa bang: {e}")
            
        conn.commit()
        print("--- DA XOA SACH 100% ---")