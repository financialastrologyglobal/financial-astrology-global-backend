from passlib.context import CryptContext

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Assuming the hashed password is retrieved from DB
stored_hashed_password = "$2b$12$8ZS.mRgWpwzZLHZX5rEkku95KR7qTA5p5xWkFUJ2XXlCU1JNpc7Xu"  # Your hash from DB

# User input password for login
input_password = "11Manav@123"

# Verify if the input password matches the stored hash
is_verified = pwd_context.verify(input_password, stored_hashed_password)
print(is_verified)  # Should print True if passwords match
