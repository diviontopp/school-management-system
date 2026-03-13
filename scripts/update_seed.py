import os
from werkzeug.security import generate_password_hash

seed_path = os.path.join("database", "seed_data.sql")
with open(seed_path, "r", encoding="utf-8") as f:
    sql = f.read()

old_hash = "$2b$12$A.PZ23VzWNr56jm0VH2u6.eHezD7Vs0nRGZmEH38dIfVKZlTbHGH6"
# Generate a standard werkzeug hash
new_hash = generate_password_hash("password123", method="pbkdf2:sha256")

if old_hash in sql:
    sql = sql.replace(old_hash, new_hash)
    with open(seed_path, "w", encoding="utf-8") as f:
        f.write(sql)
    print("Hashes updated successfully!")
else:
    print("Old hash not found.")
