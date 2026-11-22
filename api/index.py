import os
import sys

# Ensure repository root is on Python module search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.main import app, startup

# Initialize database tables and seed Pune Junction station graph if not already populated
try:
    startup()
except Exception as e:
    print(f"[Vercel Startup Warning] Database init: {e}")

# Vercel Serverless ASGI entrypoint
handler = app
