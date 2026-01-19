import sys
import os

# Add face_server to path
sys.path.append(os.path.join(os.getcwd(), 'face_server'))

try:
    from face_server.app import app
    print("SUCCESS: App imported successfully")
except ImportError as e:
    print(f"ERROR: Import failed: {e}")
except Exception as e:
    print(f"ERROR: usage failed: {e}")
