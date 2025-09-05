from fastapi import FastAPI
from dotenv import load_dotenv
from .api.router import api
from .core.security import hash_password, verify_password, create_access_token, decode_token
import os

print("Before load_dotenv():")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")

load_dotenv()

print("After load_dotenv():")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")

app = FastAPI(title="API", description="First API I've made.", version="0.1.0")
app.include_router(api)

def main():
    print("=== Testing Password Hashing ===")
    # Accept a password from the user
    password = input("Enter a password: ")

    # Hash the password
    hashed_password = hash_password(password)
    print(f"Hashed password: {hashed_password}")

    # Verify the password
    is_valid = verify_password(password, hashed_password)
    print(f"Password verification: {is_valid}")
    
    print("\n=== Testing JWT Tokens ===")
    # Create a JWT token for user ID 123
    user_id = 123
    token = create_access_token(subject=user_id)
    print(f"JWT Token: {token}")
    
    # Decode the token
    payload = decode_token(token)
    print(f"Token payload: {payload}")
    print(f"User ID from token: {payload['sub']}")

if __name__ == "__main__":
    main()
