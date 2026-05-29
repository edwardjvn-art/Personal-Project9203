"""
Run this once to generate a bcrypt hash of your password.
Then paste the output into .streamlit/secrets.toml as password_hash.

Usage:
    python hash_password.py
"""
import bcrypt
import getpass

password = getpass.getpass("Enter password to hash: ")
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(f"\nYour password hash (paste into secrets.toml):\n{hashed}")
