import sys
import os

print("--- Running Backend Diagnostics ---")
try:
    import app.main
    print("SUCCESS: app.main imported successfully!")
except Exception as e:
    print("ERROR: Failed to import app.main!")
    import traceback
    with open("diagnostic.log", "w") as f:
        traceback.print_exc(file=f)
    print("Traceback saved to diagnostic.log")
