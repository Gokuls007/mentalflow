import sys
import os
import uvicorn

# Also ensure the local app directory is in the path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

if __name__ == "__main__":
    print("Starting MentalFlow Backend...")
    print(f"System Path: {sys.path[:3]}...") # Log first few entries
    
    try:
        import sqlalchemy
        print(f"[SUCCESS] SqlAlchemy {sqlalchemy.__version__} loaded successfully.")
    except ImportError as e:
        print("[ERROR] Critical Error: Could not load SqlAlchemy. Run: pip install -r requirements.txt")
        print(e)
        sys.exit(1)

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
