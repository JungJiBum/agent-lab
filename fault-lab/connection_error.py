import socket
import time

HOST = "127.0.0.1"
PORT = 5432

print("Application started", flush=True)

while True:
    try:
        with socket.create_connection((HOST, PORT), timeout=3):
            print("Database connection successful", flush=True)
    except OSError as exc:
        print(
            f"ERROR: Database connection failed "
            f"host={HOST} port={PORT} "
            f"error={type(exc).__name__}: {exc}",
            flush=True,
        )

    time.sleep(10)