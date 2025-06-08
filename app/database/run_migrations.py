import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.migrations.remove_hashed_password import upgrade

if __name__ == "__main__":
    print("Running database migrations...")
    upgrade()
    print("Migrations completed successfully!") 