import os
import sys

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print(
        "FATAL: DATABASE_URL environment variable is required",
        file=sys.stderr,
        flush=True,
    )
    sys.exit(1)

print("Application started successfully", flush=True)