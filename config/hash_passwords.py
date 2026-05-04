import bcrypt
import sys

if len(sys.argv) < 2:
    print("Usage: python hash_passwords.py <password>")
    sys.exit(1)

password = sys.argv[1].encode('utf-8')
# Generate a salt and hash the password
hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

# Decode the hash to a string for the YAML file
print(f"Hashed Password: {hashed_password.decode('utf-8')}")
print("\nCopy this hash into your config/auth.yaml file.")
