import sqlite3
import os

# Path to your database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query all users
cursor.execute("SELECT id, username, email, google_id, storage_path FROM user")
users = cursor.fetchall()

print("=" * 80)
print("REGISTERED USERS:")
print("=" * 80)

if users:
    for user in users:
        user_id, username, email, google_id, storage_path = user
        print(f"\nUser ID: {user_id}")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Google ID: {google_id if google_id else 'Not linked'}")
        print(f"Storage Path: {storage_path}")
        print("-" * 80)
    print(f"\nTotal Users: {len(users)}")
else:
    print("\nNo users registered yet.")

print("=" * 80)

conn.close()
