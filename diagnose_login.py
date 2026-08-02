"""
EcoRoute AI - Login Diagnostic Script
Run this from the SAME folder as run.py / seed_data.py:
    python3 diagnose_login.py
"""
import os
from app import create_app
from app.models import Admin, Society, Worker

app = create_app()

print("=" * 60)
print("Working directory:", os.getcwd())
db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
print("Database URI Flask is actually using:", db_uri)

if db_uri.startswith('sqlite:///'):
    db_path = db_uri.replace('sqlite:///', '')
    print("Resolved SQLite file path:", db_path)
    print("Does that file exist?", os.path.exists(db_path))
    if os.path.exists(db_path):
        print("File size (bytes):", os.path.getsize(db_path))
        print("Last modified:", os.path.getmtime(db_path))
print("=" * 60)

with app.app_context():
    print("\n--- ADMIN ---")
    admins = Admin.query.all()
    print(f"Total admin rows: {len(admins)}")
    for a in admins:
        print(f"  email={a.email!r}  role={a.role}  password_matches_Admin123!={a.check_password('Admin123!')}")

    print("\n--- SOCIETIES ---")
    socs = Society.query.all()
    print(f"Total society rows: {len(socs)}")
    for s in socs:
        print(f"  email={s.email!r}  status={s.status}  password_matches_Society123!={s.check_password('Society123!')}")

    print("\n--- WORKERS ---")
    workers = Worker.query.all()
    print(f"Total worker rows: {len(workers)}")
    for w in workers:
        print(f"  email={w.email!r}  password_matches_Worker123!={w.check_password('Worker123!')}")

print("\n" + "=" * 60)
print("If any list above is empty (0 rows), seeding did not actually")
print("write to the database file listed above - check for a DIFFERENT")
print("ecoroute.db elsewhere, or errors during 'python3 seed_data.py'.")
print("If rows exist but password_matches is False for all, something")
print("modified the password hashing - let me know and paste this output.")
print("=" * 60)
